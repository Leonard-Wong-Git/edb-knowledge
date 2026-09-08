/**
 * routeFirstGold.ts — full 185-item gold set, FEATURE_ROUTE_FIRST_SEARCH before/after.
 *
 * Scales `routeFirstProbe.ts` (3 focused items) to the whole active gold set, and
 * keeps every one of its safety properties: host-allowlisted fetch, hard embedding
 * budget, hard request budget, and incremental save so a crash keeps what was paid for.
 *
 * WHY IN-PROCESS RATHER THAN AGAINST A LOCAL SERVER
 *   `server.ts` rate-limits 10 req/min per IP with no env override, so an HTTP run
 *   costs ~22 min per side. Calling `searchChannelB()` directly removes the limiter,
 *   embeds each query ONCE for both sides (halving model spend and removing embedding
 *   nondeterminism from the comparison), and toggles the flag between two calls that
 *   are otherwise identical — which is what a before/after gate actually requires.
 *
 * WHAT IT DOES NOT DO
 *   No scoring. Verdicts come from `dev/_s213_run_gold.py:score_item` via
 *   `dev/_s219_score_before_after.py`, so the NFKC-folding scorer stays single-sourced.
 *   `synthesize:false`, so FEATURE_GROUNDED_SYNTHESIS / FEATURE_EXACT_WINDOW_NARROW are
 *   never reached — this run gates FEATURE_ROUTE_FIRST_SEARCH only.
 *
 * READ-ONLY: search reads against live Supabase, embeddings against OpenAI. No writes,
 * no DDL, no deploy, no flag change anywhere outside this process.
 *
 * USAGE (from backend/)
 *   node_modules/.bin/tsx --env-file=.env scripts/routeFirstGold.ts
 *   node_modules/.bin/tsx --env-file=.env scripts/routeFirstGold.ts --limit 3   # smoke
 *   node_modules/.bin/tsx --env-file=.env scripts/routeFirstGold.ts --ids hr_lsp  # targeted
 */
import fs from 'node:fs';
import { searchChannelB } from '../src/api/searchChannelB.js';

const SUPABASE_HOST = 'youkcekbrbywuqjxgibe.supabase.co';
const OPENAI_HOST = 'api.openai.com';
const GOLD = '../dev/_s213_gold_all.json';
// S220 — output paths were hardcoded to the S219 filenames, so a re-run silently
// OVERWROTE the previous session's evidence. Label them instead.
const labelIdx = process.argv.indexOf('--label');
const RUN_LABEL = labelIdx > -1 ? process.argv[labelIdx + 1] : 's220';
const RUN_DATE = new Date().toISOString().slice(0, 10);
const BASE = `../dev/source/eval_runs/${RUN_DATE}_${RUN_LABEL}_route_first_before_after`;
const OUT = `${BASE}.jsonl`;
const META = `${BASE}.meta.json`;

// Budgets sized for 185 items x 2 sides. Exceeding either is a bug, not a slow run.
// Measured 1-2 embeddings per item (the expanded query is a second distinct string),
// so 185 items can legitimately need ~370. A budget of 200 would abort mid-run.
const EMBED_BUDGET = 500;
const REQUEST_BUDGET = 3000;   // ~4 Supabase calls per side per item

const limitArg = process.argv.indexOf('--limit');
const limit = limitArg > -1 ? Number(process.argv[limitArg + 1]) : undefined;

process.env.SUPABASE_URL ||= `https://${SUPABASE_HOST}`;
process.env.SUPABASE_ANON_KEY ||= process.env.SUPABASE_SERVICE_KEY;

const idsArg = process.argv.indexOf('--ids');
const onlyIds = idsArg > -1 ? new Set(process.argv[idsArg + 1].split(',')) : undefined;

const gold = JSON.parse(fs.readFileSync(GOLD, 'utf8')) as any[];
const selected = onlyIds ? gold.filter((g: any) => onlyIds.has(g.id)) : gold;
const items = limit ? selected.slice(0, limit) : selected;

let modelCalls = 0;
let requestCalls = 0;
const startedAt = new Date().toISOString();

/**
 * Routed-RPC observations for the item/mode currently running.
 *
 * WHY THIS EXISTS: `searchChannelB` wraps `searchWikiRoutedExact` in a bare
 * `catch {}` and silently keeps the legacy results. A routed RPC that 500s
 * (S214 saw `57014 canceling statement due to statement timeout` on live) is
 * therefore indistinguishable, from the outside, from a flag that ran fine and
 * changed nothing — both print `same`. Reading that as "safe to enable" would be
 * a false pass. Recording every routed call's status makes the difference legible.
 */
let routedCalls: Array<{ status: number | null; ms: number; error?: string }> = [];

/**
 * S220 — the full-corpus RPC is now the thing the flag is supposed to AVOID, so
 * it has to be measured too. Before the ordering fix both sides always called it,
 * which is why S219 only needed the routed side. Recording both lets the run show
 * (a) that flag ON calls the expensive RPC zero times, and (b) how many individual
 * calls exceed 3000ms — anon's real statement_timeout. That count is a DIRECT
 * measure of the production failure rate, replacing S219's projection from an 8s
 * ceiling, which systematically understates it.
 */
let mainCalls: Array<{ status: number | null; ms: number; error?: string }> = [];

const nativeFetch = globalThis.fetch;
globalThis.fetch = async (input: any, init?: any) => {
  const url = new URL(String(typeof input === 'string' ? input : input.url));
  if (url.hostname !== SUPABASE_HOST && url.hostname !== OPENAI_HOST) {
    throw new Error(`Request boundary: ${url.hostname}`);
  }
  if (++requestCalls > REQUEST_BUDGET) throw new Error('Request budget exhausted');
  const routed = url.pathname.endsWith('/match_wiki_chunks_routed');
  const mainRpc = url.pathname.endsWith('/match_wiki_chunks');
  const t0 = performance.now();
  try {
    const response = await nativeFetch(input, {
      ...(init ?? {}),
      signal: AbortSignal.timeout(30000),
    });
    if (routed) {
      const call: any = { status: response.status, ms: Math.round(performance.now() - t0) };
      // Capture the failure body: "same result" plus a 500 is a silent fallback, and the
      // Postgres error code is what tells us whether it is the S118 statement-timeout
      // family (57014) or something new. Clone so the caller still reads the stream.
      if (response.status !== 200) {
        try {
          call.body = (await response.clone().text()).slice(0, 300);
        } catch {
          call.body = '<unreadable>';
        }
      }
      routedCalls.push(call);
    }
    if (mainRpc) {
      const call: any = { status: response.status, ms: Math.round(performance.now() - t0) };
      if (response.status !== 200) {
        try { call.body = (await response.clone().text()).slice(0, 300); } catch { call.body = '<unreadable>'; }
      }
      mainCalls.push(call);
    }
    return response;
  } catch (e) {
    if (routed) {
      routedCalls.push({
        status: null,
        ms: Math.round(performance.now() - t0),
        error: String(e),
      });
    }
    if (mainRpc) {
      mainCalls.push({ status: null, ms: Math.round(performance.now() - t0), error: String(e) });
    }
    throw e;
  }
};

const cache = new Map<string, number[]>();
async function embed(text: string): Promise<number[]> {
  const hit = cache.get(text);
  if (hit) return hit;
  if (modelCalls >= EMBED_BUDGET) throw new Error('Embedding budget exhausted');
  modelCalls++;
  const response = await nativeFetch('https://api.openai.com/v1/embeddings', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ model: 'text-embedding-3-small', input: text }),
    signal: AbortSignal.timeout(30000),
  });
  if (!response.ok) throw new Error(`Embedding HTTP ${response.status}`);
  const data = (await response.json()) as any;
  const vec = data.data[0].embedding as number[];
  cache.set(text, vec);
  return vec;
}

/** Only the fields the Python scorer and the metrics module read. */
function pick(response: any) {
  const results = (response?.results ?? []) as any[];
  return {
    total: response?.total ?? results.length,
    degraded: response?.degraded ?? false,
    degraded_kind: response?.degraded_kind ?? null,
    results: results.map((r) => ({
      id: r.id,
      source_id: r.source_id,
      text: r.text,
      score: r.score,
      content_type: r.content_type,
      page: r.page ?? null,
    })),
  };
}

const out = fs.createWriteStream(OUT, { flags: 'w' });
const writeMeta = (status: string, error?: string) =>
  fs.writeFileSync(
    META,
    JSON.stringify(
      {
        label: `${RUN_LABEL} route-first before/after, in-process, full active gold`,
        ordering_fix: 'S220 - flag ON now REPLACES the full search instead of running after it',
        measurement_key: 'SUPABASE_ANON_KEY falls back to SERVICE key: 8s ceiling, NOT anon 3s. Count calls >3000ms for the production figure.',
        mode: 'in-process searchChannelB (no HTTP server, no rate limiter)',
        flag: 'FEATURE_ROUTE_FIRST_SEARCH',
        embedding_model: 'text-embedding-3-small',
        gold_file: GOLD,
        gold_count: items.length,
        top_k: 8,
        started_at: startedAt,
        finished_at: new Date().toISOString(),
        model_calls: modelCalls,
        request_calls: requestCalls,
        route_failures: routeFailures,
        status,
        ...(error ? { error } : {}),
      },
      null,
      1
    )
  );

let done = 0;
let errors = 0;
let routeFailures = 0;
try {
  for (const g of items) {
    const row: any = { id: g.id, query: g.query };
    for (const mode of ['before', 'after'] as const) {
      process.env.FEATURE_ROUTE_FIRST_SEARCH = mode === 'after' ? '1' : '0';
      routedCalls = [];
      mainCalls = [];
      const t0 = performance.now();
      try {
        const resp = await searchChannelB({ query: g.query, synthesize: false }, embed);
        row[mode] = pick(resp);
      } catch (e) {
        row[mode] = { error: String(e) };
        errors++;
      }
      row[`${mode}_ms`] = Math.round(performance.now() - t0);
      row[`${mode}_routed_calls`] = routedCalls;
      row[`${mode}_main_calls`] = mainCalls;
    }
    out.write(JSON.stringify(row) + '\n');
    done++;
    const changed =
      JSON.stringify((row.before?.results ?? []).map((r: any) => r.id)) !==
      JSON.stringify((row.after?.results ?? []).map((r: any) => r.id));
    const calls = row.after_routed_calls as Array<{ status: number | null }>;
    // `same` is only evidence of a benign flag when the routed RPC actually ran and
    // succeeded. No call = this query never routed; a failed call = silent fallback.
    const routeState = calls.length === 0
      ? 'no-route'
      : calls.every((c) => c.status === 200)
        ? 'routed'
        : 'ROUTE-FAILED';
    if (routeState === 'ROUTE-FAILED') routeFailures++;
    process.stdout.write(
      `[${done}/${items.length}] ${g.id.padEnd(30)} ${changed ? 'DIFF' : 'same'} ${routeState}\n`
    );
    writeMeta('running');
  }
  writeMeta('complete');
} catch (e) {
  writeMeta('aborted', String(e));
  process.stderr.write(`ABORTED after ${done}: ${String(e)}\n`);
  out.end();
  process.exit(1);
}
out.end();
process.stdout.write(
  `\n${done} items -> ${OUT} (errors=${errors}, routeFailures=${routeFailures}, ` +
    `embeddings=${modelCalls}, requests=${requestCalls})\n`
);
