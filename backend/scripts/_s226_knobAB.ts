/**
 * _s226_knobAB.ts — A/B any retrieval measurement knob over the whole active gold set.
 *
 * Started life as the per-source quota A/B (S226, `--cap`); generalised to `--set
 * KEY=VALUE` when the quota result sent the investigation to a second and third
 * knob. One harness, so the before side is produced the same way every time and
 * two runs are comparable.
 *
 * The S226 diagnosis found 16 of 61 right-document-wrong-passage items where the
 * answering chunk out-scored the 8th returned chunk while its source sat exactly
 * at maxPerSource (3 of 8). This runs the real `searchChannelB` twice per item —
 * once with the production formula, once with MAX_PER_SOURCE — and records both
 * windows so `_s219_score_before_after.py` scores them with the same NFKC scorer
 * everything else in this project uses.
 *
 * INVARIANT ASSERTED FIRST, BEFORE ANY SPEND: with MAX_PER_SOURCE unset,
 * `capFromEnv` must return undefined, i.e. the default path is the old formula.
 * The knob is for measuring the cap, not for changing it.
 *
 * Same safety properties as routeFirstGold.ts: host-allowlisted fetch, hard
 * embedding budget, one embedding shared by both sides, incremental save.
 *
 * READ-ONLY: search reads against live Supabase, embeddings against OpenAI.
 *
 * USAGE (from backend/)
 *   node_modules/.bin/tsx --env-file=.env scripts/_s226_knobAB.ts \
 *       --set MAX_PER_SOURCE=8 --label s226cap8
 *   node_modules/.bin/tsx --env-file=.env scripts/_s226_knobAB.ts \
 *       --set FEATURE_LEXICAL_RERANK=1 --label s226rerank
 *   node_modules/.bin/tsx --env-file=.env scripts/_s226_knobAB.ts \
 *       --set FAMILY_QUOTA=1 --label s226family
 */
import fs from 'node:fs';
import { searchChannelB, capFromEnv } from '../src/api/searchChannelB.js';

const SUPABASE_HOST = 'youkcekbrbywuqjxgibe.supabase.co';
const OPENAI_HOST = 'api.openai.com';
const GOLD = '../dev/_s213_gold_all.json';

// --- invariants, checked before a single token is spent ---------------------
// Every knob here is off-by-default by construction. The one with a value rather
// than a flag gets its parser asserted, because "unset means unchanged" is the
// whole basis for calling these measurement knobs instead of changes.
for (const bad of [undefined, '', '  ', '0', '-1', '3.5', 'eight', '3x']) {
  if (capFromEnv(bad as any) !== undefined) {
    throw new Error(`capFromEnv must ignore ${JSON.stringify(bad)}`);
  }
}
if (capFromEnv('8') !== 8 || capFromEnv(' 4 ') !== 4) {
  throw new Error('capFromEnv must read a positive integer');
}
process.stdout.write('invariant OK: MAX_PER_SOURCE unset / malformed => production formula\n');

// --set KEY=VALUE, repeatable. These are applied to the AFTER side only, and
// deleted again before the next item, so the before side is always the shipped
// configuration rather than whatever the previous iteration left behind.
const KNOBS: Array<[string, string]> = [];
for (let i = 0; i < process.argv.length; i++) {
  if (process.argv[i] !== '--set') continue;
  const pair = process.argv[i + 1] ?? '';
  const eq = pair.indexOf('=');
  if (eq < 1) throw new Error(`--set needs KEY=VALUE, got ${JSON.stringify(pair)}`);
  KNOBS.push([pair.slice(0, eq), pair.slice(eq + 1)]);
}
if (KNOBS.length === 0) throw new Error('nothing to A/B: pass at least one --set KEY=VALUE');
for (const [k] of KNOBS) {
  if (process.env[k] !== undefined) {
    throw new Error(`${k} is already set in the environment; the before side would not be the shipped configuration`);
  }
}
const labelIdx = process.argv.indexOf('--label');
const RUN_LABEL = labelIdx > -1 ? process.argv[labelIdx + 1] : 's226knob';
const limitArg = process.argv.indexOf('--limit');
const limit = limitArg > -1 ? Number(process.argv[limitArg + 1]) : undefined;

const RUN_DATE = new Date().toISOString().slice(0, 10);
const BASE = `../dev/source/eval_runs/${RUN_DATE}_${RUN_LABEL}_before_after`;
const OUT = `${BASE}.jsonl`;
const META = `${BASE}.meta.json`;

process.env.SUPABASE_URL ||= `https://${SUPABASE_HOST}`;
process.env.SUPABASE_ANON_KEY ||= process.env.SUPABASE_SERVICE_KEY;
// production state for the flag under test elsewhere: route-first is ON in prod
// (S226 verified behaviourally, 184/184), so both sides here run with it ON.
process.env.FEATURE_ROUTE_FIRST_SEARCH = '1';

const EMBED_BUDGET = 500;
const REQUEST_BUDGET = 4000;
let modelCalls = 0;
let requestCalls = 0;

const nativeFetch = globalThis.fetch;
globalThis.fetch = async (input: any, init?: any) => {
  const url = new URL(String(typeof input === 'string' ? input : input.url));
  if (url.hostname !== SUPABASE_HOST && url.hostname !== OPENAI_HOST) {
    throw new Error(`Request boundary: ${url.hostname}`);
  }
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
    headers: {
      Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ model: 'text-embedding-3-small', input: text }),
    signal: AbortSignal.timeout(30000),
  });
  if (!r.ok) throw new Error(`Embedding HTTP ${r.status}`);
  const vec = ((await r.json()) as any).data[0].embedding as number[];
  cache.set(text, vec);
  return vec;
}

function pick(response: any) {
  const results = (response?.results ?? []) as any[];
  return {
    total: response?.total ?? results.length,
    degraded: response?.degraded ?? false,
    degraded_kind: response?.degraded_kind ?? null,
    results: results.map((r) => ({
      id: r.id, source_id: r.source_id, text: r.text,
      score: r.score, content_type: r.content_type, page: r.page ?? null,
    })),
  };
}

const gold = JSON.parse(fs.readFileSync(GOLD, 'utf8')) as any[];
const items = limit ? gold.slice(0, limit) : gold;
const out = fs.createWriteStream(OUT, { flags: 'w' });
const startedAt = new Date().toISOString();
let done = 0, errors = 0, changed = 0;

const writeMeta = (status: string, error?: string) =>
  fs.writeFileSync(META, JSON.stringify({
    label: `${RUN_LABEL}: before=shipped configuration vs after=${KNOBS.map(([k, v]) => `${k}=${v}`).join(' ')}`,
    knobs: Object.fromEntries(KNOBS),
    invariant: 'every knob is off/unset on the before side and deleted between items; MAX_PER_SOURCE parser asserted at startup',
    measurement_key: 'SUPABASE_ANON_KEY falls back to SERVICE key: 8s ceiling, NOT anon 3s',
    mode: 'in-process searchChannelB, FEATURE_ROUTE_FIRST_SEARCH=1 on both sides',
    embedding_model: 'text-embedding-3-small', gold_file: GOLD, gold_count: items.length,
    top_k: 8, started_at: startedAt, finished_at: new Date().toISOString(),
    model_calls: modelCalls, request_calls: requestCalls, changed_windows: changed,
    status, ...(error ? { error } : {}),
  }, null, 1));

try {
  for (const g of items) {
    const row: any = { id: g.id, query: g.query };
    for (const mode of ['before', 'after'] as const) {
      if (mode === 'after') for (const [k, v] of KNOBS) process.env[k] = v;
      else for (const [k] of KNOBS) delete process.env[k];
      const t0 = performance.now();
      try {
        row[mode] = pick(await searchChannelB({ query: g.query, synthesize: false }, embed));
      } catch (e) {
        row[mode] = { error: String(e) };
        errors++;
      }
      row[`${mode}_ms`] = Math.round(performance.now() - t0);
    }
    for (const [k] of KNOBS) delete process.env[k];
    out.write(JSON.stringify(row) + '\n');
    done++;
    const diff = JSON.stringify((row.before?.results ?? []).map((r: any) => r.id)) !==
                 JSON.stringify((row.after?.results ?? []).map((r: any) => r.id));
    if (diff) changed++;
    process.stdout.write(`[${done}/${items.length}] ${g.id.padEnd(32)} ${diff ? 'DIFF' : 'same'}\n`);
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
process.stdout.write(`\n${done} items -> ${OUT} (errors=${errors}, changed=${changed}, embeddings=${modelCalls}, requests=${requestCalls})\n`);
