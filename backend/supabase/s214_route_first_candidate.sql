-- S214 isolated candidate installation. No table or existing RPC changes.
begin;
-- 6b. Route-first exact search ------------------------------------------------
-- Separately named to avoid a PostgREST overload ambiguity with match_wiki_chunks.
-- The sequential scan is intentional: source filtering must happen before ranking, and
-- the route subsets are bounded (the largest current set is about 3,500 chunks). Baseline:
-- 17,602 total chunks on 2026-09-06; re-evaluate latency and scan strategy as the store grows.
create or replace function public.match_wiki_chunks_routed(
  query_embedding  text,
  source_ids       text[],
  match_threshold  double precision default 0.1,
  match_count      integer          default null
)
returns table (
  id text, hash text, text text, source_id text, title text, url text, topic text,
  content_type text, fact_type text, role text, school_level text,
  reference_year text, score double precision
)
language plpgsql
volatile
as $$
begin
  set local enable_indexscan = off;
  set local enable_bitmapscan = off;
  return query
    select
      wc.id, wc.hash, wc.text, wc.source_id, wc.title, wc.url, wc.topic,
      wc.content_type, wc.fact_type, wc.role, wc.school_level, wc.reference_year,
      round((1 - (wc.embedding <=> query_embedding::vector))::numeric, 4)::float as score
    from public.wiki_chunks wc
    where wc.source_id = any(source_ids)
      and 1 - (wc.embedding <=> query_embedding::vector) >= match_threshold
    order by wc.embedding <=> query_embedding::vector
    limit match_count;
end;
$$;

grant execute on function public.match_wiki_chunks_routed(text, text[], double precision, integer) to anon;
grant execute on function public.match_wiki_chunks_routed(text, text[], double precision, integer) to authenticated;

commit;

