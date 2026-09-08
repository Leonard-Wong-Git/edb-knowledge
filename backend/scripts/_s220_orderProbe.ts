/**
 * S220 — proves the route-first ordering fix: flag ON must call the routed RPC
 * ONLY, never the full-corpus one. Same query, same cached embedding, both runs.
 * NOTE: like routeFirstProbe.ts this measures under the SERVICE key (8s ceiling),
 * not anon's real 3s. Latencies are comparable to each other, not to production.
 */
import { searchChannelB } from '../src/api/searchChannelB.js';
process.env.SUPABASE_URL ||= 'https://youkcekbrbywuqjxgibe.supabase.co';
process.env.SUPABASE_ANON_KEY ||= process.env.SUPABASE_SERVICE_KEY;

const nativeFetch = globalThis.fetch;
let calls: { path: string; ms: number }[] = [];
globalThis.fetch = async (input: any, init: any) => {
  const url = new URL(String(input));
  const start = performance.now();
  try { return await nativeFetch(input, init); }
  finally {
    if (url.hostname.includes('supabase')) {
      calls.push({ path: url.pathname.split('/').pop()!, ms: Math.round(performance.now() - start) });
    }
  }
};

const cache = new Map<string, number[]>();
async function embed(text: string): Promise<number[]> {
  if (cache.has(text)) return cache.get(text)!;
  const r = await nativeFetch('https://api.openai.com/v1/embeddings', {
    method: 'POST',
    headers: { Authorization: `Bearer ${process.env.OPENAI_API_KEY}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ model: 'text-embedding-3-small', input: text }),
  });
  const body = await r.text();
  let parsed: any;
  try { parsed = JSON.parse(body); } catch { throw new Error(`embed non-JSON ${r.status}: ${body.slice(0, 300)}`); }
  if (!parsed?.data?.[0]?.embedding) throw new Error(`embed ${r.status}: ${body.slice(0, 300)}`);
  const v = parsed.data[0].embedding as number[];
  cache.set(text, v); return v;
}

const QUERY = '教師專業發展 課時要求';
async function run(label: string, flag: string) {
  process.env.FEATURE_ROUTE_FIRST_SEARCH = flag;
  calls = [];
  const t0 = performance.now();
  let res: any = null; let err: string | null = null;
  try { res = await searchChannelB({ query: QUERY, top_k: 50, synthesize: false } as any, embed as any); }
  catch (e: any) { err = String(e?.message ?? e).slice(0, 160); }
  const ms = Math.round(performance.now() - t0);
  const n = err ? `ERROR — ${err}` : (Array.isArray(res?.results) ? res.results.length : (res?.total ?? '?'));
  console.log(`\n  ${label} (FEATURE_ROUTE_FIRST_SEARCH=${flag})`);
  console.log(`    總耗時 ${ms}ms · 回 ${n} 條`);
  const rpc = calls.filter(c => c.path.startsWith('match_wiki_chunks'));
  for (const c of rpc) console.log(`      → ${c.path}  ${c.ms}ms`);
  console.log(`    全庫 RPC 被呼叫: ${rpc.filter(c => c.path === 'match_wiki_chunks').length} 次`);
  console.log(`    路由 RPC 被呼叫: ${rpc.filter(c => c.path === 'match_wiki_chunks_routed').length} 次`);
  return ms;
}
(async () => {
  await embed(QUERY);                       // warm the embedding cache once
  const off1 = await run('修正後 · flag OFF 第 1 次（現行生產路徑）', '0');
  const on1  = await run('修正後 · flag ON  第 1 次（應只打路由 RPC）', '1');
  const off2 = await run('修正後 · flag OFF 第 2 次', '0');
  const on2  = await run('修正後 · flag ON  第 2 次', '1');
  console.log(`\n  OFF: ${off1}ms / ${off2}ms      ON: ${on1}ms / ${on2}ms\n`);
})();
