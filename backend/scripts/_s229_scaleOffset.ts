/**
 * _s229_scaleOffset.ts — where does VAULT_LEAD_SCORE 0.70 sit on the scale it is
 * actually APPLIED to?
 *
 * WHY THIS EXISTS. `VAULT_LEAD_SCORE = 0.70` (searchChannelB.ts:1422, gate at :1242)
 * was calibrated by `dev/source/judge_probe.py`, and that probe embeds the BARE query
 * and queries the WHOLE index (`match_threshold 0.1, match_count 40`, no SOURCE_SET).
 * Production applies the same number to `mainSearchLead.score`, which comes from a
 * search that embeds `expandQuery(query, detectedCategory)` (:1657) and narrows to the
 * routed SOURCE_SET with `effectiveMinScore` 0.08 (:1652). Two different scales.
 *
 * S229 established statically that this affects 97 of 185 gold queries (the routed
 * ones); the other 88 are unrouted, where expanded === bare and the two scales coincide.
 * This probe measures the OFFSET on the 24 queries the bar was actually set with, so
 * the recalibration in Open Priorities ②(c) can use a measured equivalent quantile
 * instead of a guess.
 *
 * THREE SCALES, ALL PRODUCED BY PRODUCTION CODE — nothing is re-implemented here:
 *   A  bare query,     whole index   — judge_probe.py's method = the calibration scale
 *   B  bare query,     routed        — searchChannelB with an embedFn pinned to the bare
 *                                      vector, so routing is isolated from expansion
 *   C  expanded query, routed        — searchChannelB unmodified = the applied scale
 *
 * A->B isolates the routing narrowing, B->C isolates the expansion. Changing both at
 * once is the S222/S223 mistake this project has already paid for twice.
 *
 * READ-ONLY: embeddings + the same read-only RPC the gold harness runs. `synthesize`
 * is false, so no synthesizer and no judge calls. Writes nothing to Supabase.
 *
 * USAGE (from backend/)
 *   node_modules/.bin/tsx --env-file=.env scripts/_s229_scaleOffset.ts <out.json>
 */
import fs from 'node:fs';
import { searchChannelB, detectQueryCategory } from '../src/api/searchChannelB.js';

const SUPABASE_HOST = 'youkcekbrbywuqjxgibe.supabase.co';
const OPENAI_HOST = 'api.openai.com';
process.env.SUPABASE_URL ||= `https://${SUPABASE_HOST}`;
// Measurement key note (Risks 2b): this falls back to the SERVICE key's 8s ceiling,
// not anon's 3s. Scores are unaffected; failure RATES measured here would be optimistic.
process.env.SUPABASE_ANON_KEY ||= process.env.SUPABASE_SERVICE_KEY;
// Production has FEATURE_ROUTE_FIRST_SEARCH=1 (Render env, S220). `_s226_knobAB.ts:139`
// sets it for the same reason: without it `routeFirst` at searchChannelB.ts:1715 is
// false and the routed path measured here is NOT the one production runs.
process.env.FEATURE_ROUTE_FIRST_SEARCH = '1';

/**
 * The exact three classes `dev/source/judge_probe.py` uses, copied verbatim from that
 * file (CLASS_A/B/C). They are the set the 0.70 bar was set with, so re-measuring them
 * on the applied scale is the apples-to-apples comparison; any other set would be
 * answering a different question (claim discipline L3).
 */
const CLASS_A = [
  '香港股票市場今日收市指數',
  '米線湯底煮法食譜',
  '英超足球聯賽賽程表',
  '比特幣今年價格走勢',
  '台灣高鐵時刻表同票價',
  'iPhone 換電池保養價錢',
];
const CLASS_B = [
  '教師每年可以請幾多日大假',
  '校長退休金點樣計',
  '解僱教師要俾幾多個月遣散費',
  '幼稚園每班最多可以收幾多個學生',
  '學校泳池水質檢測標準係咩',
  '老師病假連續請幾耐先要交醫生紙',
  '學校可唔可以借錢俾教職員',
  '校巴司機最低工資係幾多',
  '學生喺校內可以用手機幾耐',
  '教師評核幾多分先算合格',
  '學校每堂補習費可以收幾多',
  '校服供應商招標要幾多間報價',
  '體罰投訴要幾多日內處理完',
  '課室冷氣應該調到幾多度',
];
const CLASS_C = [
  '人工智能初探',
  '資訊及通訊科技 課程指引',
  '跟車保母有咩要求',
  '校巴司機安全指引',
];

const CLASSES: Array<[string, string[]]> = [
  ['A off-domain', CLASS_A],
  ['B plausible-gap', CLASS_B],
  ['C positive control', CLASS_C],
];

const EMBED_BUDGET = 120;
const REQUEST_BUDGET = 400;
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
async function realEmbed(text: string): Promise<number[]> {
  const hit = cache.get(text);
  if (hit) return hit;
  if (++modelCalls > EMBED_BUDGET) throw new Error('Embedding budget exhausted');
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

/** Scale A — judge_probe.py's exact method: bare vector, whole index, no narrowing. */
async function wholeIndexTopVault(vec: number[]): Promise<number | null> {
  const body = {
    query_embedding: '[' + vec.map((x) => x.toFixed(8)).join(',') + ']',
    match_threshold: 0.1,
    match_count: 40,
  };
  const key = process.env.SUPABASE_SERVICE_KEY as string;
  const r = await nativeFetch(`https://${SUPABASE_HOST}/rest/v1/rpc/match_wiki_chunks`, {
    method: 'POST',
    headers: { apikey: key, Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
    signal: AbortSignal.timeout(90000),
  });
  if (!r.ok) throw new Error(`RPC HTTP ${r.status}`);
  const rows = (await r.json()) as any[];
  for (const row of rows) {
    if (row.content_type === 'vault_extract') return row.score as number;
  }
  return null;
}

/** Top vault_extract score in the window searchChannelB returns. */
function topVaultInWindow(resp: any): number | null {
  for (const r of resp?.results ?? []) {
    if (r.content_type === 'vault_extract') return r.score as number;
  }
  return null;
}

const out: any[] = [];

for (const [label, queries] of CLASSES) {
  for (const query of queries) {
    const category = detectQueryCategory(query);

    // Scale C — production, unmodified. Capture every string it asks to embed.
    const asked: string[] = [];
    const respC = await searchChannelB(
      { query, synthesize: false },
      async (text: string) => {
        asked.push(text);
        return realEmbed(text);
      }
    );

    const bareVec = await realEmbed(query);

    // Scale B — same routed search, but every embed request answered with the BARE
    // vector. Routing is therefore identical to C while the vector is identical to A.
    const respB = await searchChannelB({ query, synthesize: false }, async () => bareVec);

    // Scale A — whole index, bare vector.
    const a = await wholeIndexTopVault(bareVec);
    const b = topVaultInWindow(respB);
    const c = topVaultInWindow(respC);

    const expanded = asked.find((s) => s !== query) ?? null;
    out.push({
      class: label,
      query,
      category,
      routed: category !== null,
      expanded,
      scale_A_bare_whole_index: a,
      scale_B_bare_routed: b,
      scale_C_expanded_routed: c,
    });
    const f = (v: number | null) => (v === null ? '  none' : v.toFixed(4));
    console.log(
      `${label.padEnd(20)} ${(category ?? '-').padEnd(18)} A=${f(a)} B=${f(b)} C=${f(c)}  ${query}`
    );
  }
}

const outPath = process.argv[2] ?? 'scripts/_s229_scaleOffset.out.json';
fs.writeFileSync(
  outPath,
  JSON.stringify(
    {
      label: 'S229 — VAULT_LEAD_SCORE calibration-scale vs applied-scale offset',
      instrument: 'production searchChannelB + judge_probe.py whole-index method',
      calibration_set: 'dev/source/judge_probe.py CLASS_A/B/C, verbatim',
      embedding_model: 'text-embedding-3-small',
      measurement_key: 'SUPABASE_ANON_KEY falls back to SERVICE key: 8s ceiling, not anon 3s',
      synthesize: false,
      model_calls: modelCalls,
      request_calls: requestCalls,
      finished_at: new Date().toISOString(),
      rows: out,
    },
    null,
    1
  )
);
console.log(`\nwrote ${outPath} · embeds=${modelCalls} requests=${requestCalls}`);
