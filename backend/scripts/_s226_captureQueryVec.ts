/**
 * _s226_captureQueryVec.ts — record the exact string the backend embeds for ranking.
 *
 * WHY THIS EXISTS: S226's chunk-layer diagnosis needs the score the RPC WOULD have
 * given the answering chunk, which means using the same query vector production
 * ranks by. That vector is not the raw query: `searchChannelB` embeds
 * `expandQuery(query, detectedCategory)`, and `QUERY_EXPANSIONS` is module-private.
 * Re-implementing the expansion in Python would be a port of ranking logic — the
 * class of thing this project has been burned by. So instead of porting, pass an
 * `embedFn` that CAPTURES what the backend asks for and returns the real embedding.
 * Zero divergence by construction.
 *
 * A first pass with the raw query disagreed with the recorded scores on 17 of 61
 * items by up to 0.19 — which is exactly what an unrecorded expansion looks like.
 *
 * READ-ONLY: embeddings + the same read-only search the gold harness runs.
 *
 * USAGE (from backend/)
 *   node_modules/.bin/tsx --env-file=.env scripts/_s226_captureQueryVec.ts <ids.json> <out.json>
 */
import fs from 'node:fs';
import { searchChannelB, detectQueryCategory } from '../src/api/searchChannelB.js';

const SUPABASE_HOST = 'youkcekbrbywuqjxgibe.supabase.co';
const OPENAI_HOST = 'api.openai.com';
process.env.SUPABASE_URL ||= `https://${SUPABASE_HOST}`;
process.env.SUPABASE_ANON_KEY ||= process.env.SUPABASE_SERVICE_KEY;

const [idsPath, outPath] = process.argv.slice(2);
const items: Array<{ id: string; query: string }> = JSON.parse(fs.readFileSync(idsPath, 'utf8'));

const EMBED_BUDGET = 200;
let modelCalls = 0;
const nativeFetch = globalThis.fetch;
globalThis.fetch = async (input: any, init?: any) => {
  const url = new URL(String(typeof input === 'string' ? input : input.url));
  if (url.hostname !== SUPABASE_HOST && url.hostname !== OPENAI_HOST) {
    throw new Error(`Request boundary: ${url.hostname}`);
  }
  return nativeFetch(input, { ...(init ?? {}), signal: AbortSignal.timeout(30000) });
};

async function realEmbed(text: string): Promise<number[]> {
  if (++modelCalls > EMBED_BUDGET) throw new Error('embedding budget exhausted');
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
  return ((await r.json()) as any).data[0].embedding as number[];
}

const out: any[] = [];
for (const [i, item] of items.entries()) {
  // Every string the backend asks to embed, in order, WITH its vector. Which one
  // the ranking used is not assumed here: the first pass guessed "the last" and
  // was wrong — `searchChannelB` embeds the EXPANDED query first and the raw
  // query after it (24 of 63 items expand to the same string, so the order only
  // shows up on the other 39). The caller decides by control: recompute a
  // returned chunk's cosine against each candidate and keep the one that matches
  // the score the run recorded.
  const asked: Array<{ text: string; vec: number[] }> = [];
  const capture = async (text: string) => {
    const vec = await realEmbed(text);
    asked.push({ text, vec });
    return vec;
  };
  let resp: any = null;
  let error: string | null = null;
  try {
    resp = await searchChannelB({ query: item.query, synthesize: false }, capture);
  } catch (e) {
    error = String(e);
  }
  out.push({
    id: item.id,
    query: item.query,
    detected_category: detectQueryCategory(item.query),
    embedded: asked.map((a, i) => ({ i, text: a.text, vec: a.vec })),
    returned: (resp?.results ?? []).map((r: any) => ({ id: r.id, source_id: r.source_id, score: r.score })),
    ...(error ? { error } : {}),
  });
  process.stdout.write(
    `[${i + 1}/${items.length}] ${item.id.padEnd(34)} route=${String(detectQueryCategory(item.query))} ` +
      `embedded=${asked.length}${asked.length && asked[asked.length - 1].text !== item.query ? ' (expanded)' : ''}\n`
  );
}
fs.writeFileSync(outPath, JSON.stringify(out));
process.stdout.write(`\nwrote ${outPath} (embeddings=${modelCalls})\n`);
