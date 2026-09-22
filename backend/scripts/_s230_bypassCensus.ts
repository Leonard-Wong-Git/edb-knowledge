/**
 * _s230_bypassCensus.ts — who actually gets the vault judge-bypass, and is each one right?
 *
 * WHY THIS EXISTS. `_s230_gateSignalAB.ts` measured the bypass on the 24 queries that set
 * the 0.70 bar and found five of them bypassing. Five points cannot validate any gate, and
 * that probe has no ground truth: it knows a query is CLASS_B, not whether the answer was
 * in the window. The 185-item gold set carries both (`answerable`, `expected_source_any`,
 * `expected_passage_signature`, `forbidden_evidence`), so this census answers the question
 * the A/B could only pose: of the queries that bypass the judge today, how many are the
 * S177 class — the judge skipped and the window holding no answer?
 *
 * ONE ARM, AND WHY THAT IS SOUND. The candidate flag is ON here, not to measure it, but
 * because with the flag on the gate reads the lead chunk back by primary key, so
 * intercepting that one URL names the exact chunk the gate tested and hands over its
 * vector for free. From that single run:
 *   bypass_before  = the lead is a vault_extract (implied: the gate only reads back then)
 *                    AND its applied score >= 0.70 — the pre-change expression, evaluated
 *                    on observed inputs rather than re-implemented.
 *   bypass_after   = OBSERVED, via a stub judge that records whether it was consulted.
 * The derivation was validated against the two-arm run before being relied on here: on all
 * 24 rows of 2026-09-21_s230_gate_signal_ab.json the derived value equals the observed
 * `bypass_before`, 24/24, and every row had a lead chunk. The flag changes the comparison,
 * not the searches or the lead selection, so the two arms see the same lead.
 *
 * The bare query vector is taken from the embedding call `searchChannelB` already makes for
 * its overlay passes (captured in the same fetch wrapper), so this adds no embedding calls
 * beyond the two the production path makes per query.
 *
 * READ-ONLY. Stub synthesiser and stub judge: no answer model, no judge model, no writes.
 *
 * USAGE (from backend/)
 *   node_modules/.bin/tsx --env-file=.env scripts/_s230_bypassCensus.ts --self-test
 *   node_modules/.bin/tsx --env-file=.env scripts/_s230_bypassCensus.ts <out.json> [--limit N]
 */
import fs from 'node:fs';
import { searchChannelB, detectQueryCategory } from '../src/api/searchChannelB.js';
import { overlapWith, queryInformativeBigrams } from '../src/lib/textBigrams.js';
import { footnoteInformativeBigrams } from '../src/lib/wikiRepository.js';

const SUPABASE_HOST = 'youkcekbrbywuqjxgibe.supabase.co';
const OPENAI_HOST = 'api.openai.com';
process.env.SUPABASE_URL ||= `https://${SUPABASE_HOST}`;
process.env.SUPABASE_ANON_KEY ||= process.env.SUPABASE_SERVICE_KEY;
process.env.FEATURE_ROUTE_FIRST_SEARCH = '1';

const VAULT_BAR = 0.70;

type Gold = {
  id: string; query: string; domain?: string; answerable: boolean;
  expected_source_any?: string[]; expected_passage_signature?: string[];
  forbidden_evidence?: string[];
};

/**
 * Ground-truth verdict for ONE query that bypasses the judge today. The three outcomes
 * are kept apart because they need different fixes and a single count would hide that:
 *   FALSE_BYPASS   gold says the corpus cannot answer this. Judge skipped, synthesiser
 *                  handed a window with no answer — the S177 class the bar exists to stop.
 *   WRONG_PASSAGE  answerable, but no expected passage signature appears in the window.
 *                  Right register, wrong text: also a false-answer risk, and the reason
 *                  the chunk layer is Open Priority 2 in the first place.
 *   SOUND          answerable and an expected signature is in the window.
 */
export function bypassVerdict(
  answerable: boolean,
  signatureInWindow: boolean | null
): 'FALSE_BYPASS' | 'WRONG_PASSAGE' | 'SOUND' | 'UNKNOWN' {
  if (!answerable) return 'FALSE_BYPASS';
  if (signatureInWindow === null) return 'UNKNOWN';
  return signatureInWindow ? 'SOUND' : 'WRONG_PASSAGE';
}

/**
 * The candidate rule shape recorded in the handoff for a later session: block the bypass
 * only when the query HAS informative bigrams and the window contains NONE of them.
 * `null` bigram count means the measure cannot judge (an English or bare-noun query) and
 * must therefore let the bypass stand — textBigrams.ts states that rule explicitly, and
 * folding it into "no overlap" would refuse exactly the queries the bypass rescues.
 */
export function zeroOverlapWouldBlock(queryBigrams: number, overlap: number): boolean {
  if (queryBigrams === 0) return false;
  return overlap === 0;
}

function selfTest(): number {
  let fails = 0;
  const ok = (n: string, c: boolean) => { if (!c) { fails++; console.log(`  FAIL ${n}`); } else console.log(`  ok   ${n}`); };

  ok('unanswerable bypass is a false bypass', bypassVerdict(false, true) === 'FALSE_BYPASS');
  ok('unanswerable verdict ignores the window', bypassVerdict(false, null) === 'FALSE_BYPASS');
  ok('answerable with signature in window is sound', bypassVerdict(true, true) === 'SOUND');
  ok('answerable without signature is wrong passage', bypassVerdict(true, false) === 'WRONG_PASSAGE');
  ok('no signature to check reports UNKNOWN', bypassVerdict(true, null) === 'UNKNOWN');

  ok('zero overlap blocks when the query is judgeable', zeroOverlapWouldBlock(3, 0) === true);
  ok('some overlap does not block', zeroOverlapWouldBlock(3, 1) === false);
  // RED-TEST ASSERTION — the rule must NOT block a query it cannot judge. 人工智能初探 has
  // no informative bigrams and is a positive control whose bypass must survive; if this
  // ever returns true the rule has become a blanket refusal for bare-noun queries.
  ok('a query with no informative bigrams is never blocked', zeroOverlapWouldBlock(0, 0) === false);

  console.log(fails === 0 ? '\nALL PASS' : `\n${fails} FAILED`);
  return fails === 0 ? 0 : 1;
}

if (process.argv.includes('--self-test')) process.exit(selfTest());

const GATE_URL_RE = /\/rest\/v1\/wiki_chunks\?id=eq\.([^&]+)&select=embedding/;
const nativeFetch = globalThis.fetch;
let gateRead: { id: string; embedding: number[] } | null = null;
const embedCache = new Map<string, number[]>();
let embedCalls = 0;

globalThis.fetch = async (input: any, init?: any) => {
  const raw = String(typeof input === 'string' ? input : input.url);
  const url = new URL(raw);
  if (url.hostname !== SUPABASE_HOST && url.hostname !== OPENAI_HOST) {
    throw new Error(`Request boundary: ${url.hostname}`);
  }
  const resp = await nativeFetch(input, { ...(init ?? {}), signal: AbortSignal.timeout(30000) });
  if (url.hostname === OPENAI_HOST && url.pathname === '/v1/embeddings' && resp.ok) {
    embedCalls++;
    try {
      const sent = JSON.parse(String((init ?? {}).body ?? '{}'));
      const got = (await resp.clone().json()) as any;
      if (typeof sent.input === 'string') embedCache.set(sent.input, got.data[0].embedding as number[]);
    } catch { /* capture is best-effort; a miss only costs one extra embed below */ }
  }
  const m = GATE_URL_RE.exec(raw);
  if (m && resp.ok) {
    const rows = (await resp.clone().json()) as Array<{ embedding: unknown }>;
    const e = rows.length ? rows[0].embedding : null;
    gateRead = {
      id: decodeURIComponent(m[1]),
      embedding: typeof e === 'string' ? (JSON.parse(e) as number[]) : ((e as number[]) ?? []),
    };
  }
  return resp;
};

async function embed(text: string): Promise<number[]> {
  const hit = embedCache.get(text);
  if (hit) return hit;
  const r = await nativeFetch('https://api.openai.com/v1/embeddings', {
    method: 'POST',
    headers: { Authorization: `Bearer ${process.env.OPENAI_API_KEY}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ model: 'text-embedding-3-small', input: text }),
    signal: AbortSignal.timeout(30000),
  });
  if (!r.ok) throw new Error(`Embedding HTTP ${r.status}`);
  embedCalls++;
  const v = ((await r.json()) as any).data[0].embedding as number[];
  embedCache.set(text, v);
  return v;
}

function cosine4(a: number[], b: number[]): number {
  let dot = 0, na = 0, nb = 0;
  const n = Math.min(a.length, b.length);
  for (let i = 0; i < n; i++) { dot += a[i] * b[i]; na += a[i] * a[i]; nb += b[i] * b[i]; }
  const c = na && nb ? dot / (Math.sqrt(na) * Math.sqrt(nb)) : 0;
  // 4dp, matching match_wiki_chunks (dev/supabase_setup.sql:69) — the scale the bar was set on.
  return Math.round(c * 1e4) / 1e4;
}

const out = process.argv.find((a) => a.endsWith('.json') && !a.startsWith('--'));
const limitArg = process.argv.indexOf('--limit');
const limit = limitArg > 0 ? Number(process.argv[limitArg + 1]) : undefined;

const gold = JSON.parse(fs.readFileSync('../dev/_s213_gold_all.json', 'utf8')) as Gold[];
const cases = limit ? gold.slice(0, limit) : gold;
const stop = await footnoteInformativeBigrams();
process.env.FEATURE_VAULT_GATE_RAWVEC = '1';

const rows: any[] = [];
let n = 0;
for (const g of cases) {
  n++;
  gateRead = null;
  let judgeCalls = 0;
  const judgeFn = async (_p: string) => { judgeCalls++; return '能'; };
  const llmFn = async (_p: string) => 'STUB_SYNTHESIS';

  let resp: any;
  try {
    resp = await searchChannelB({ query: g.query, synthesize: true }, embed, llmFn, judgeFn);
  } catch (e) {
    rows.push({ id: g.id, query: g.query, error: String(e).slice(0, 160) });
    console.log(`[${n}/${cases.length}] ERROR ${g.id}: ${String(e).slice(0, 80)}`);
    continue;
  }
  const rs = (resp.results ?? []) as any[];
  const windowRows = rs.slice(0, 5);
  const windowText = windowRows.map((r) => r.text).join('\n');

  const lead = gateRead as { id: string; embedding: number[] } | null;
  const appliedRow = lead ? rs.find((r) => r.id === lead.id) : undefined;
  const applied = appliedRow ? appliedRow.score : null;
  const bare = lead && lead.embedding.length ? cosine4(await embed(g.query), lead.embedding) : null;

  const bypassBefore = !!lead && applied !== null && applied >= VAULT_BAR;
  const bypassAfter = judgeCalls === 0;

  const bigrams = queryInformativeBigrams(g.query, stop);
  const overlap = overlapWith(bigrams, windowText);

  const sigs = g.expected_passage_signature ?? [];
  const signatureInWindow = !g.answerable || sigs.length === 0
    ? null
    : sigs.some((sig) => windowText.includes(sig));
  const expectedSourceInWindow = (g.expected_source_any ?? []).length === 0
    ? null
    : windowRows.some((r) => (g.expected_source_any ?? []).includes(r.source_id));
  const forbiddenInWindow = (g.forbidden_evidence ?? []).length === 0
    ? null
    : windowRows.some((r) => (g.forbidden_evidence ?? []).includes(r.source_id));

  const row = {
    id: g.id, query: g.query, domain: g.domain ?? null, route: detectQueryCategory(g.query) ?? null,
    answerable: g.answerable,
    lead_chunk_id: lead?.id ?? null, lead_source_id: appliedRow?.source_id ?? null,
    applied_scale_score: applied, bare_scale_score: bare,
    bypass_before: bypassBefore, bypass_after: bypassAfter,
    query_bigrams: bigrams.size, window_overlap: overlap,
    zero_overlap_would_block: zeroOverlapWouldBlock(bigrams.size, overlap),
    signature_in_window: signatureInWindow,
    expected_source_in_window: expectedSourceInWindow,
    forbidden_source_in_window: forbiddenInWindow,
    bypass_verdict: bypassBefore ? bypassVerdict(g.answerable, signatureInWindow) : null,
  };
  rows.push(row);
  if (bypassBefore) {
    console.log(
      `[${n}/${cases.length}] BYPASS ${String(row.bypass_verdict).padEnd(13)} applied ${(applied ?? 0).toFixed(4)}` +
      ` bare ${bare === null ? '  -   ' : bare.toFixed(4)} overlap ${overlap}/${bigrams.size}` +
      `${row.zero_overlap_would_block ? ' WOULD-BLOCK' : ''}  ${g.query}`
    );
  } else if (n % 25 === 0) {
    console.log(`[${n}/${cases.length}] ...`);
  }
}

const bypassed = rows.filter((r) => r.bypass_before);
const byVerdict = (v: string) => bypassed.filter((r) => r.bypass_verdict === v);
const blocked = bypassed.filter((r) => r.zero_overlap_would_block);
const summary = {
  bar: VAULT_BAR,
  cases: rows.length,
  errors: rows.filter((r) => r.error).length,
  vault_lead: rows.filter((r) => r.lead_chunk_id).length,
  bypass_before: bypassed.length,
  bypass_after_rawvec_gate: rows.filter((r) => r.bypass_after).length,
  verdicts: {
    FALSE_BYPASS: byVerdict('FALSE_BYPASS').length,
    WRONG_PASSAGE: byVerdict('WRONG_PASSAGE').length,
    SOUND: byVerdict('SOUND').length,
    UNKNOWN: byVerdict('UNKNOWN').length,
  },
  // The 2x2 the candidate rule has to be judged on: does it block the bypasses that are
  // wrong, and leave alone the ones that are right?
  zero_overlap_rule: {
    would_block_total: blocked.length,
    blocks_FALSE_BYPASS: blocked.filter((r) => r.bypass_verdict === 'FALSE_BYPASS').length,
    blocks_WRONG_PASSAGE: blocked.filter((r) => r.bypass_verdict === 'WRONG_PASSAGE').length,
    blocks_SOUND: blocked.filter((r) => r.bypass_verdict === 'SOUND').length,
    blocks_UNKNOWN: blocked.filter((r) => r.bypass_verdict === 'UNKNOWN').length,
    leaves_FALSE_BYPASS: byVerdict('FALSE_BYPASS').filter((r) => !r.zero_overlap_would_block).length,
    unjudgeable_bypasses: bypassed.filter((r) => r.query_bigrams === 0).length,
  },
  embedding_calls: embedCalls,
};
console.log('\n' + JSON.stringify(summary, null, 2));

if (out) {
  fs.writeFileSync(out, JSON.stringify({ summary, rows }, null, 2));
  console.log(`\nwrote ${out}`);
}
