/**
 * _s241_circularAB.ts — before/after for FEATURE_CIRCULAR_NUMBER_LOOKUP (S241).
 *
 * Runs the production search function locally (FEATURE_ROUTE_FIRST_SEARCH=1, as on
 * Render) twice per query — flag unset, then flag on — and records where the circular
 * the query names lands in the eight results. synthesize:false: embeddings only, zero LLM.
 * Also proves the flag is inert for every 185-gold query (the parser returns null).
 *
 * USAGE (from backend/)
 *   node_modules/.bin/tsx --env-file=.env scripts/_s241_circularAB.ts
 */
import fs from 'node:fs';
import { parseCircularRef } from '../src/lib/circularRef.js';

const SUPABASE_HOST = 'youkcekbrbywuqjxgibe.supabase.co';
const OPENAI_HOST = 'api.openai.com';
process.env.SUPABASE_URL ||= `https://${SUPABASE_HOST}`;
process.env.SUPABASE_ANON_KEY ||= process.env.SUPABASE_SERVICE_KEY;
process.env.FEATURE_ROUTE_FIRST_SEARCH = '1'; // production state

const nativeFetch = globalThis.fetch;
globalThis.fetch = async (input: any, init?: any) => {
  const url = new URL(String(typeof input === 'string' ? input : input.url));
  if (url.hostname !== SUPABASE_HOST && url.hostname !== OPENAI_HOST) {
    throw new Error(`Request boundary: ${url.hostname}`);
  }
  return nativeFetch(input, { ...(init ?? {}), signal: AbortSignal.timeout(30000) });
};

const EMBED_BUDGET = 260;
let embedCalls = 0;
const embCache = new Map<string, number[]>();
async function embed(text: string): Promise<number[]> {
  const hit = embCache.get(text);
  if (hit) return hit;
  if (++embedCalls > EMBED_BUDGET) throw new Error('Embedding budget exhausted');
  const r = await nativeFetch('https://api.openai.com/v1/embeddings', {
    method: 'POST',
    headers: { Authorization: `Bearer ${process.env.OPENAI_API_KEY}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ model: 'text-embedding-3-small', input: text }),
    signal: AbortSignal.timeout(30000),
  });
  if (!r.ok) throw new Error(`Embedding HTTP ${r.status}`);
  const vec = ((await r.json()) as any).data[0].embedding as number[];
  embCache.set(text, vec);
  return vec;
}

const { searchChannelB } = await import('../src/api/searchChannelB.js');
const { loadCircularIndex } = await import('../src/lib/wikiRepository.js');

// Gold inertness: the flag can only change a query the parser recognises.
const gold = JSON.parse(fs.readFileSync('../dev/_s213_gold_all.json', 'utf8')) as Array<{ id: string; query: string }>;
const goldTriggers = gold.filter((g) => parseCircularRef(g.query) !== null).map((g) => g.id);

const index = await loadCircularIndex();
const keys = [...index.keys()].sort();
const queries: Array<{ key: string; form: string; query: string }> = [];
for (const key of keys) {
  const [kind, n, y] = key.split('|');
  queries.push({ key, form: 'canonical', query: `教育局${kind}第${n}/${y}號` });
}
// Phrasings users actually type, on the 2026 memoranda (the circular in the S241 decline).
for (const key of keys.filter((k) => k.startsWith('通函|') && k.endsWith('|2026')).slice(0, 8)) {
  const [, n, y] = key.split('|');
  queries.push({ key, form: 'short', query: `通函${n}/${y}` });
  queries.push({ key, form: 'english', query: `EDBCM ${n}/${y}` });
  queries.push({ key, form: 'with_topic', query: `通函第${n}/${y}號 學校要做甚麼` });
}

const rankOf = (res: any[], sid: string) => {
  const i = res.findIndex((r) => r.source_id === sid);
  return i < 0 ? null : i;
};
const rows: any[] = [];
for (const q of queries) {
  const sid = index.get(q.key)!;
  delete process.env.FEATURE_CIRCULAR_NUMBER_LOOKUP;
  const before = await searchChannelB({ query: q.query, synthesize: false } as any, embed as any);
  process.env.FEATURE_CIRCULAR_NUMBER_LOOKUP = '1';
  const after = await searchChannelB({ query: q.query, synthesize: false } as any, embed as any);
  delete process.env.FEATURE_CIRCULAR_NUMBER_LOOKUP;
  rows.push({
    ...q, source_id: sid,
    before: rankOf(before.results, sid), after: rankOf(after.results, sid),
    after_top: after.results.slice(0, 5).map((r: any) => r.source_id),
  });
}

const sum = (side: 'before' | 'after') => ({
  rank0: rows.filter((r) => r[side] === 0).length,
  window5: rows.filter((r) => r[side] !== null && r[side] < 5).length,
  absent: rows.filter((r) => r[side] === null).length,
});
const report = {
  generated_at: new Date().toISOString(),
  config: 'FEATURE_ROUTE_FIRST_SEARCH=1, synthesize:false, local service key',
  index_size: index.size, queries: rows.length, embed_calls: embedCalls,
  gold_queries: gold.length, gold_queries_that_trigger: goldTriggers,
  before: sum('before'), after: sum('after'),
  by_form: Object.fromEntries(['canonical', 'short', 'english', 'with_topic'].map((f) => {
    const sub = rows.filter((r) => r.form === f);
    return [f, { n: sub.length, before_window5: sub.filter((r) => r.before !== null && r.before < 5).length, after_rank0: sub.filter((r) => r.after === 0).length }];
  })),
  regressions: rows.filter((r) => r.before !== null && (r.after === null || r.after > r.before)),
  rows,
};
const out = `../dev/source/eval_runs/${report.generated_at.slice(0, 10)}_s241_circular_ab.json`;
fs.writeFileSync(out, JSON.stringify(report, null, 1) + '\n');
console.log(JSON.stringify({ ...report, rows: undefined }, null, 1));
console.log('wrote', out);
