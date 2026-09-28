-- S233 — search log + answer feedback (DRAFT, not yet applied)
-- ════════════════════════════════════════════════════════════
-- Purpose: keep every real Channel B search (query, route, answer, result window) for 180
-- days so retrieval work can be measured against what users actually ask, and let users
-- rate an answer 👍/👎. Design: dev/SEARCH_LOG_DESIGN.md.
--
-- Pattern copied from the S204 usage counter (usage_daily + bump_usage):
--   - the backend holds only the anon key, so writes go through SECURITY DEFINER functions
--     with EXECUTE granted to anon; the table itself has RLS on and NO policy, so anon can
--     neither read nor write it directly.
--   - do NOT revoke anon on the functions: the S204 first draft did and would have blocked
--     the backend (CODEBASE_CONTEXT, usage counter notes).
-- Reading is service_role only (Dashboard / Claude's local scripts); it bypasses RLS.
--
-- Pre-apply check done 2026-09-28 (S233): public.search_log → PGRST205 (absent);
-- rpc/log_search and rpc/record_search_feedback → PGRST202 (absent). New names, no
-- create-or-replace of an existing function, so no PGRST203 overload risk.
-- Apply via Supabase Dashboard SQL Editor (Claude cannot run DDL, PMS §D.18).

create table if not exists public.search_log (
  id           uuid primary key,
  created_at   timestamptz not null default now(),
  query        text        not null,
  client       text,                 -- 'desktop' | 'mobile' | null (server-to-server)
  route        text,                 -- detectQueryCategory() result, null = no route
  declined     boolean     not null default false,  -- synthesis was the decline text
  degraded     boolean     not null default false,  -- Channel B could not contribute
  synthesis    text,                 -- answer shown to the user, full text
  results      jsonb       not null default '[]'::jsonb,  -- result window, see design doc
  total        integer,
  latency_ms   integer,
  feedback     smallint    check (feedback in (-1, 1)),
  feedback_at  timestamptz
);

create index if not exists search_log_created_at_idx on public.search_log (created_at);

alter table public.search_log enable row level security;
-- Intentionally no policy: anon/authenticated get nothing on the table.

-- ── Write one search ─────────────────────────────────────────────────────────
-- Caps every field so a caller holding the anon key cannot bloat the table. Purges rows
-- older than 180 days on each insert: at ~5 searches/day the delete touches nothing most
-- of the time, and this avoids depending on pg_cron (not verified on this project).
create or replace function public.log_search(
  p_id         uuid,
  p_query      text,
  p_client     text,
  p_route      text,
  p_declined   boolean,
  p_degraded   boolean,
  p_synthesis  text,
  p_results    jsonb,
  p_total      integer,
  p_latency_ms integer
) returns void
language plpgsql
security definer
set search_path = public
as $$
begin
  insert into public.search_log (
    id, query, client, route, declined, degraded, synthesis, results, total, latency_ms
  ) values (
    p_id,
    left(coalesce(p_query, ''), 500),
    left(p_client, 20),
    left(p_route, 60),
    coalesce(p_declined, false),
    coalesce(p_degraded, false),
    left(p_synthesis, 4000),
    case
      when jsonb_typeof(p_results) = 'array' and pg_column_size(p_results) <= 65536
        then p_results
      else '[]'::jsonb
    end,
    p_total,
    p_latency_ms
  )
  on conflict (id) do nothing;

  delete from public.search_log where created_at < now() - interval '180 days';
end;
$$;

-- ── Record 👍/👎 on one answer ───────────────────────────────────────────────
-- Accepts only an existing row younger than 24 hours; a later click overwrites an earlier
-- one (the user changed their mind). Returns whether a row was updated.
create or replace function public.record_search_feedback(
  p_id     uuid,
  p_rating smallint
) returns boolean
language plpgsql
security definer
set search_path = public
as $$
begin
  if p_rating is null or p_rating not in (-1, 1) then
    return false;
  end if;
  update public.search_log
     set feedback = p_rating, feedback_at = now()
   where id = p_id
     and created_at > now() - interval '24 hours';
  return found;
end;
$$;

grant execute on function public.log_search(uuid, text, text, text, boolean, boolean, text, jsonb, integer, integer) to anon;
grant execute on function public.record_search_feedback(uuid, smallint) to anon;

-- ── Post-apply verification (run after the DDL, expect the values in comments) ─
-- select count(*) from public.search_log;                                   -- 0
-- select relrowsecurity from pg_class where oid = 'public.search_log'::regclass;  -- true
-- select count(*) from pg_policies where tablename = 'search_log';          -- 0
