/**
 * _s229_leadDetail.ts — does the judge-bypass actually FIRE on the three adversarial
 * queries that cross 0.70 on the applied scale?
 *
 * `_s229_scaleOffset.ts` measured "top vault_extract anywhere in the window". The gate
 * at searchChannelB.ts:1240-1242 is narrower: it tests `mainSearchLead`, which is
 * `results.find(...)` taken at :1748 BEFORE any overlay is prepended — i.e. the single
 * highest-scoring non-stat chunk of the routed main search — and requires that chunk to
 * be `vault_extract` with score >= 0.70. Crossing 0.70 is therefore necessary but not
 * sufficient, and this script closes that gap instead of leaving it assumed.
 *
 * METHOD. Overlays are PREPENDED (searchChannelB.ts:1843-1847 splices spotlight in at
 * `forcedLeads`), so the main-search portion of the window is the maximal descending
 * suffix. Printing the whole window with content_type and score makes the forced prefix
 * visible and lets the main-search lead be identified by inspection rather than inferred.
 *
 * READ-ONLY, synthesize:false — no synthesizer, no judge.
 *
 * USAGE (from backend/)
 *   node_modules/.bin/tsx --env-file=.env scripts/_s229_leadDetail.ts
 */
import { searchChannelB, detectQueryCategory } from '../src/api/searchChannelB.js';

const SUPABASE_HOST = 'youkcekbrbywuqjxgibe.supabase.co';
const OPENAI_HOST = 'api.openai.com';
process.env.SUPABASE_URL ||= `https://${SUPABASE_HOST}`;
process.env.SUPABASE_ANON_KEY ||= process.env.SUPABASE_SERVICE_KEY;
// Production has FEATURE_ROUTE_FIRST_SEARCH=1 (Render env, S220). `_s226_knobAB.ts:139`
// sets it for the same reason: without it `routeFirst` at searchChannelB.ts:1715 is
// false and the routed path measured here is NOT the one production runs.
process.env.FEATURE_ROUTE_FIRST_SEARCH = '1';

/** The CLASS_B (plausible-gap: answer NOT in corpus) queries at or near the 0.70 bar. */
const QUERIES = [
  '老師病假連續請幾耐先要交醫生紙',
  '校巴司機最低工資係幾多',
  '解僱教師要俾幾多個月遣散費',
  // one control for contrast — its answer IS in the corpus
  '跟車保母有咩要求',
];

const nativeFetch = globalThis.fetch;
globalThis.fetch = async (input: any, init?: any) => {
  const url = new URL(String(typeof input === 'string' ? input : input.url));
  if (url.hostname !== SUPABASE_HOST && url.hostname !== OPENAI_HOST) {
    throw new Error(`Request boundary: ${url.hostname}`);
  }
  return nativeFetch(input, { ...(init ?? {}), signal: AbortSignal.timeout(30000) });
};

async function embed(text: string): Promise<number[]> {
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

const VAULT_BAR = 0.70;

for (const query of QUERIES) {
  const resp: any = await searchChannelB({ query, synthesize: false }, embed);
  const rs = (resp.results ?? []) as any[];
  console.log(`\n=== ${query}   [route: ${detectQueryCategory(query) ?? '-'}]`);

  // The forced prefix ends where the remaining scores become monotonically descending.
  let mainStart = 0;
  for (let i = 0; i < rs.length; i++) {
    let descending = true;
    for (let j = i + 1; j < rs.length; j++) {
      if (rs[j].score > rs[j - 1].score + 1e-12) {
        descending = false;
        break;
      }
    }
    if (descending) {
      mainStart = i;
      break;
    }
  }

  rs.forEach((r, i) => {
    const tag = i < mainStart ? 'FORCED' : i === mainStart ? 'MAIN-LEAD' : '';
    console.log(
      `  [${i}] ${r.score.toFixed(4)}  ${String(r.content_type).padEnd(18)} ${String(r.source_id).padEnd(26)} ${tag}`
    );
  });

  const lead = rs[mainStart];
  const fires = !!lead && lead.content_type === 'vault_extract' && lead.score >= VAULT_BAR;
  console.log(
    `  -> main-search lead: ${lead ? `${lead.content_type} @ ${lead.score.toFixed(4)}` : 'none'}` +
      `  | judge-bypass fires: ${fires ? 'YES — judge SKIPPED' : 'no — judge runs'}`
  );
}
