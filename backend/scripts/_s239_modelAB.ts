/**
 * _s239_modelAB.ts — answer-layer A/B of the SYNTHESIS + JUDGE models, same retrieval.
 *
 * WHY A SEPARATE HARNESS. `_s226_knobAB.ts` builds its LLM clients once at startup, so
 * it can A/B anything read per request (flags) but not the model, which is fixed when
 * the client is created. This builds two client pairs and calls the real
 * `searchChannelB(request, embed, llm, judge)` once per side, so the only variable is
 * the model pair:
 *   before = --before-model (synthesis) + --before-judge, no reasoning field. Explicit
 *            because the code defaults moved to gpt-6-luna in S239 — reading them here
 *            would now compare the new model with itself.
 *   after  = --after-model for both, `reasoning.effort` = --after-effort
 * Retrieval is identical on both sides by construction (one embedding cache, same
 * code, same flags); the run asserts the two windows are equal and records it.
 *
 * Output is the `_s226_knobAB.ts --synthesize` JSONL shape, so `_s227_rubricJudge.ts`
 * scores it unchanged. Each LLM call is timed per side (`*_llm_ms`), because the
 * retiring models are being replaced on cost AND latency, not quality alone.
 *
 * SPEND GATE. `--approved-max-llm-calls=N` is mandatory and counted across both sides
 * before each call; embeddings have their own cap. READ-ONLY against Supabase.
 *
 * USAGE (from backend/)
 *   node_modules/.bin/tsx --env-file=.env scripts/_s239_modelAB.ts \
 *     --before-model gpt-4o-mini --before-judge gpt-4.1-mini --after-model gpt-6-luna --after-effort none --sample 36 \
 *     --approved-max-llm-calls=144 --label s239model
 */
import fs from 'node:fs';
import { searchChannelB } from '../src/api/searchChannelB.js';
import { createLlmClient } from '../src/lib/llmClient.js';
import { reasoningEffortFromEnv } from '../src/config/env.js';

const SUPABASE_HOST = 'youkcekbrbywuqjxgibe.supabase.co';
const OPENAI_HOST = 'api.openai.com';
const GOLD = '../dev/_s213_gold_all.json';

const arg = (name: string): string | undefined => {
  const inline = process.argv.find((a) => a.startsWith(`--${name}=`));
  if (inline) return inline.slice(name.length + 3);
  const i = process.argv.indexOf(`--${name}`);
  return i > -1 ? process.argv[i + 1] : undefined;
};

const BEFORE_MODEL = arg('before-model') ?? 'gpt-4o-mini';
const BEFORE_JUDGE = arg('before-judge') ?? 'gpt-4.1-mini';
const AFTER_MODEL = arg('after-model');
const AFTER_EFFORT = reasoningEffortFromEnv(arg('after-effort'));
const SAMPLE = Number(arg('sample') ?? 0);
const APPROVED = Number(arg('approved-max-llm-calls'));
const LABEL = arg('label') ?? 's239model';
if (!AFTER_MODEL) throw new Error('--after-model is required');
if (!Number.isInteger(APPROVED) || APPROVED <= 0) {
  throw new Error('External API approval required: pass --approved-max-llm-calls=N only after Leonard approves.');
}
if (!Number.isInteger(SAMPLE) || SAMPLE <= 0) throw new Error('--sample N is required');
if (process.env.OPENAI_REASONING_EFFORT || process.env.JUDGE_REASONING_EFFORT) {
  throw new Error('reasoning-effort env vars are set; the before side would not be the shipped configuration');
}

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

const EMBED_BUDGET = 200;
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

let llmCalls = 0;
type Fn = (prompt: string, format?: any) => Promise<string>;
// searchChannelB swallows a failed synthesis call and returns an empty answer (S237), so
// a model error would read as "no answer". Every failure is recorded per side instead.
function metered(fn: Fn, sink: number[], errs: string[]): Fn {
  return async (prompt, format) => {
    if (++llmCalls > APPROVED) throw new Error(`LLM call budget ${APPROVED} exhausted`);
    const t = Date.now();
    try {
      return await fn(prompt, format);
    } catch (e) {
      errs.push(String(e).slice(0, 200));
      throw e;
    } finally {
      sink.push(Date.now() - t);
    }
  };
}

const baseLlm = createLlmClient({ model: BEFORE_MODEL, maxRetries: 0 });
const baseJudge = createLlmClient({ model: BEFORE_JUDGE, maxRetries: 0 });
const newLlm = createLlmClient({ model: AFTER_MODEL, reasoningEffort: AFTER_EFFORT, maxRetries: 0 });
const newJudge = createLlmClient({ model: AFTER_MODEL, reasoningEffort: AFTER_EFFORT, maxRetries: 0 });

// Evenly spaced over the whole gold set, so every domain and the no-answer items appear.
const gold = JSON.parse(fs.readFileSync(GOLD, 'utf8')) as any[];
const picks = [...new Set(Array.from({ length: SAMPLE }, (_, k) =>
  Math.round((k * (gold.length - 1)) / Math.max(1, SAMPLE - 1))))].map((i) => gold[i]);

const DATE = new Date().toISOString().slice(0, 10);
const BASE = `../dev/source/eval_runs/${DATE}_${LABEL}_before_after`;
fs.writeFileSync(`${BASE}.jsonl`, '');
const ids = (r: any) => (r?.results ?? []).map((x: any) => x.id);
const window = (r: any) => ({ total: r?.total ?? 0, results: (r?.results ?? []).map((x: any) => ({
  id: x.id, source_id: x.source_id, score: x.score, content_type: x.content_type, page: x.page ?? null })) });

let windowsDiffer = 0;
let errors = 0;
for (const [n, g] of picks.entries()) {
  const row: any = { id: g.id, query: g.query };
  try {
    const bMs: number[] = [];
    const aMs: number[] = [];
    const bErr: string[] = [];
    const aErr: string[] = [];
    const before = await searchChannelB({ query: g.query, synthesize: true }, embed as any,
      metered(baseLlm, bMs, bErr), metered(baseJudge, bMs, bErr));
    const after = await searchChannelB({ query: g.query, synthesize: true }, embed as any,
      metered(newLlm, aMs, aErr), metered(newJudge, aMs, aErr));
    if (bErr.length || aErr.length) errors++;
    const same = JSON.stringify(ids(before)) === JSON.stringify(ids(after));
    if (!same) windowsDiffer++;
    Object.assign(row, {
      before: window(before), before_synthesis: before.synthesis ?? null, before_llm_ms: bMs, before_llm_errors: bErr,
      after: window(after), after_synthesis: after.synthesis ?? null, after_llm_ms: aMs, after_llm_errors: aErr,
      windows_identical: same,
    });
  } catch (e) {
    errors++;
    row.error = String(e);
  }
  fs.appendFileSync(`${BASE}.jsonl`, JSON.stringify(row) + '\n');
  process.stdout.write(`[${n + 1}/${picks.length}] ${g.id.padEnd(36)} ${row.error ? 'ERROR ' + row.error.slice(0, 60) : row.windows_identical ? 'same-window' : 'WINDOW-DIFF'}\n`);
  if (String(row.error ?? '').includes('budget')) break;
}

fs.writeFileSync(`${BASE}.meta.json`, JSON.stringify({
  label: LABEL,
  before: { synthesis_model: BEFORE_MODEL, judge_model: BEFORE_JUDGE, reasoning: 'not sent' },
  after: { synthesis_model: AFTER_MODEL, judge_model: AFTER_MODEL, reasoning_effort: AFTER_EFFORT ?? 'not sent' },
  sample: picks.length, approved_max_llm_calls: APPROVED, llm_calls: llmCalls, embed_calls: embedCalls,
  windows_differ: windowsDiffer, errors, mode: 'in-process searchChannelB, FEATURE_ROUTE_FIRST_SEARCH=1',
  measurement_key: 'SUPABASE_ANON_KEY falls back to SERVICE key: 8s ceiling, NOT anon 3s',
  finished_at: new Date().toISOString(),
}, null, 1));
process.stdout.write(`\nllm_calls=${llmCalls} embed_calls=${embedCalls} windows_differ=${windowsDiffer} errors=${errors}\n`);
