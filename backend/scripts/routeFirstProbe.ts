import fs from 'node:fs';
import { searchChannelB } from '../src/api/searchChannelB.js';

const output = '../dev/source/eval_runs/2026-09-07_s214_route_first_focused.json';
const gold = JSON.parse(fs.readFileSync('../dev/_s213_gold_all.json', 'utf8'));
const ids = ['hr_lsp', 'sen_special_school_curriculum', 'ss_ncs_history_adapted_outline_v2'];
process.env.SUPABASE_URL ||= 'https://youkcekbrbywuqjxgibe.supabase.co';
process.env.SUPABASE_ANON_KEY ||= process.env.SUPABASE_SERVICE_KEY;
const nativeFetch = globalThis.fetch;
const trace: any[] = [];
const cases: any[] = [];
let modelCalls = 0;
let current = '';
const save = () => fs.writeFileSync(output, JSON.stringify({ model: 'text-embedding-3-small', modelCalls, trace, cases }, null, 2));
globalThis.fetch = async (input, init) => {
  const url = new URL(String(input));
  if (url.hostname !== 'youkcekbrbywuqjxgibe.supabase.co' || trace.length >= 60) throw new Error('Probe request boundary');
  const row: any = { case: current, path: url.pathname, status: null, ms: null };
  trace.push(row);
  save();
  const start = performance.now();
  try {
    const response = await nativeFetch(input, { ...init, signal: AbortSignal.timeout(25000) });
    row.status = response.status;
    if (url.pathname.endsWith('/match_wiki_chunks_routed')) {
      const data = await response.clone().json();
      row.rows = Array.isArray(data) ? data.map((x: any) => ({ id: x.id, score: x.score })) : data;
    }
    return response;
  } finally { row.ms = Math.round(performance.now() - start); save(); }
};
const cache = new Map<string, number[]>();
async function embed(text: string): Promise<number[]> {
  if (cache.has(text)) return cache.get(text)!;
  if (modelCalls >= 6) throw new Error('Embedding budget exhausted');
  modelCalls++; save();
  const response = await nativeFetch('https://api.openai.com/v1/embeddings', {
    method: 'POST',
    headers: { Authorization: `Bearer ${process.env.OPENAI_API_KEY}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ model: 'text-embedding-3-small', input: text }),
    signal: AbortSignal.timeout(25000),
  });
  if (!response.ok) throw new Error(`Embedding HTTP ${response.status}`);
  const data = await response.json() as any;
  cache.set(text, data.data[0].embedding);
  return cache.get(text)!;
}
for (const id of ids) {
  const g = gold.find((x: any) => x.id === id);
  const item: any = { id, query: g.query };
  cases.push(item);
  for (const mode of ['before', 'after']) {
    current = `${id}:${mode}`;
    process.env.FEATURE_ROUTE_FIRST_SEARCH = mode === 'after' ? '1' : '0';
    const start = performance.now();
    try { item[mode] = await searchChannelB({ query: g.query, synthesize: false }, embed); }
    catch (e) { item[mode] = { error: String(e) }; }
    item[`${mode}Ms`] = Math.round(performance.now() - start);
    save();
  }
  console.log(JSON.stringify({ id, before: item.before.results?.map((r: any) => r.id), after: item.after.results?.map((r: any) => r.id), beforeMs: item.beforeMs, afterMs: item.afterMs }));
}
console.log(JSON.stringify({ modelCalls, requests: trace.length, routed: trace.filter(x => x.path.endsWith('/match_wiki_chunks_routed')).map(x => ({ case: x.case, status: x.status, ms: x.ms })) }));
