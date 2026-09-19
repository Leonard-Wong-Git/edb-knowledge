/**
 * _s228_rerankCeiling.ts — how much of the chunk-layer gap could ANY re-ranker close?
 *
 * WHY (Open Priorities ②). After S228 excluded a fourth direction, the two untried
 * ones are a cross-encoder re-rank and length-adaptive expansion. Length-adaptive is
 * now measured. A cross-encoder costs a model call per candidate per query, so before
 * anyone builds one the honest question is: of the items whose answering passage is
 * missing from the top 8, how many are present in the wider pool a re-ranker would
 * actually see? A passage that is not in the pool cannot be re-ranked into it, and
 * that count is the ceiling on the whole direction.
 *
 * WHAT IT MEASURES. Per gold item with a passage signature: the rank of the
 * answering chunk at the production window (top_k=8) and in a wide pool (top_k=40,
 * which is the over-fetch `searchWikiRoutedExact` already performs — fetchCount =
 * topK*5 — so the pool is one a re-ranker could be inserted into without a second
 * retrieval).
 *
 * WHAT IT IS NOT. It does not re-rank anything and calls no judge or cross-encoder.
 * It reports an upper bound, not an expected gain: being in the pool is necessary,
 * not sufficient. The per-source quota also widens with top_k (max(2, ceil(k/3))),
 * so the wide pool is more permissive than production's — that too inflates the
 * bound in the optimistic direction, which is the safe direction for a ceiling.
 *
 * READ-ONLY: live Supabase reads + OpenAI embeddings. No writes, no model judging.
 *
 * USAGE (from backend/)
 *   node_modules/.bin/tsx --env-file=.env scripts/_s228_rerankCeiling.ts --self-test
 *   node_modules/.bin/tsx --env-file=.env scripts/_s228_rerankCeiling.ts --label s228ceiling
 */
import fs from 'node:fs';
import { searchChannelB } from '../src/api/searchChannelB.js';

const SUPABASE_HOST = 'youkcekbrbywuqjxgibe.supabase.co';
const OPENAI_HOST = 'api.openai.com';
const GOLD = '../dev/_s213_gold_all.json';
const NARROW_K = 8;
const WIDE_K = 40;

// Production config, set before the self-test so the self-test can assert it.
process.env.FEATURE_ROUTE_FIRST_SEARCH = '1';

const arg = (n: string) => { const i = process.argv.indexOf(n); return i > -1 ? process.argv[i + 1] : undefined; };

/**
 * NO SCORING HERE. The NFKC-folding, marker-stripping signature match lives in
 * `dev/_s213_run_gold.py:score_item` and nowhere else; a TypeScript copy would be a
 * second definition of the same rule and the two would drift (AGENTS §3b, and the
 * same reason `routeFirstGold.ts` refuses to score). This file captures the two
 * windows; `dev/_s228_ceiling_report.py` ranks them with the shared scorer.
 */
function selfTest(): number {
  const fails: string[] = [];
  const ok = (l: string, c: boolean) => { process.stdout.write(`  ${c ? 'PASS' : 'FAIL'}  ${l}\n`); if (!c) fails.push(l); };
  ok('生產配置：FEATURE_ROUTE_FIRST_SEARCH 必須為 1（S227 曾量錯一次生產不執行的配置）',
    process.env.FEATURE_ROUTE_FIRST_SEARCH === '1');
  ok('寬池必須真的比窗闊，否則量到的只是同一個窗', WIDE_K > NARROW_K);
  ok('寬池要對得上 searchWikiRoutedExact 的 over-fetch（topK*5 = 40）', NARROW_K * 5 === WIDE_K);
  // 這條斷言守住「唔好喺 TS 再寫一份判分規則」。搜尋字串要喺執行時砌，
  // 否則斷言自己嗰行就會命中自己，永遠紅。
  const foldToken = 'norm' + 'alize(';
  const own = fs.readFileSync(new URL(import.meta.url)).toString();
  ok('本檔不得自行判分：原始碼不可出現 Unicode fold 呼叫（判分屬 _s213_run_gold.py）',
    own.split(foldToken).length - 1 === 0);
  process.stdout.write(`\n${fails.length ? `${fails.length} FAILED` : 'ALL PASS'}\n`);
  return fails.length ? 1 : 0;
}
if (process.argv.includes('--self-test')) process.exit(selfTest());

const RUN_LABEL = arg('--label') ?? 's228ceiling';
const OUT = `../dev/source/eval_runs/${new Date().toISOString().slice(0, 10)}_${RUN_LABEL}.json`;
const EMBED_BUDGET = 500;
const REQUEST_BUDGET = 3000;

process.env.SUPABASE_URL ||= `https://${SUPABASE_HOST}`;
process.env.SUPABASE_ANON_KEY ||= process.env.SUPABASE_SERVICE_KEY;

let modelCalls = 0, requestCalls = 0;
const nativeFetch = globalThis.fetch;
globalThis.fetch = async (input: any, init?: any) => {
  const url = new URL(String(typeof input === 'string' ? input : input.url));
  if (url.hostname !== SUPABASE_HOST && url.hostname !== OPENAI_HOST) throw new Error(`Request boundary: ${url.hostname}`);
  if (++requestCalls > REQUEST_BUDGET) throw new Error('Request budget exhausted');
  return nativeFetch(input, { ...(init ?? {}), signal: AbortSignal.timeout(30000) });
};
const cache = new Map<string, number[]>();
async function embed(text: string): Promise<number[]> {
  const hit = cache.get(text);
  if (hit) return hit;
  if (modelCalls >= EMBED_BUDGET) throw new Error('Embedding budget exhausted');
  modelCalls++;
  const r = await nativeFetch('https://api.openai.com/v1/embeddings', {
    method: 'POST',
    headers: { Authorization: `Bearer ${process.env.OPENAI_API_KEY}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ model: 'text-embedding-3-small', input: text }),
    signal: AbortSignal.timeout(30000),
  });
  if (!r.ok) throw new Error(`Embedding HTTP ${r.status}`);
  const vec = ((await r.json()) as any).data[0].embedding as number[];
  cache.set(text, vec);
  return vec;
}

const gold = (JSON.parse(fs.readFileSync(GOLD, 'utf8')) as any[])
  .filter((g) => g.answerable && (g.expected_passage_signature ?? []).length > 0);

const rows: any[] = [];
let done = 0;
for (const g of gold) {
  const row: any = { id: g.id, query: g.query, query_kind: g.query_kind, domain: g.domain };
  for (const [name, k] of [['narrow', NARROW_K], ['wide', WIDE_K]] as const) {
    try {
      const resp: any = await searchChannelB({ query: g.query, synthesize: false, top_k: k }, embed);
      const results = (resp?.results ?? []) as any[];
      row[name] = {
        total: resp?.total ?? results.length,
        results: results.map((r) => ({
          id: r.id, source_id: r.source_id, text: r.text,
          score: r.score, content_type: r.content_type, page: r.page ?? null,
        })),
      };
    } catch (e) {
      row[name] = { error: String(e) };
    }
  }
  rows.push(row);
  done++;
  process.stdout.write(
    `[${done}/${gold.length}] ${g.id.padEnd(32)} narrow=${row.narrow?.results?.length ?? 'ERR'} `
    + `wide=${row.wide?.results?.length ?? 'ERR'}\n`
  );
}

fs.writeFileSync(OUT, JSON.stringify({
  label: `${RUN_LABEL} — cross-encoder re-rank ceiling capture`,
  generated_at: new Date().toISOString(),
  gold_file: GOLD, narrow_k: NARROW_K, wide_k: WIDE_K,
  production_config: 'FEATURE_ROUTE_FIRST_SEARCH=1',
  scoring: 'none here — run dev/_s228_ceiling_report.py, which uses _s213_run_gold.score_item',
  quota_caveat: 'maxPerSource widens with top_k (max(2, ceil(k/3))), so the wide pool is more '
    + 'permissive than production. That inflates the ceiling in the optimistic direction.',
  model_calls: modelCalls, request_calls: requestCalls,
  items: rows.length, results: rows,
}, null, 1));
process.stdout.write(`\n${rows.length} items -> ${OUT}\n`
  + `now: python3 dev/_s228_ceiling_report.py --capture ${OUT.replace('../', '')}\n`);
