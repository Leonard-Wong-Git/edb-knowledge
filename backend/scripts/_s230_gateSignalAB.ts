/**
 * _s230_gateSignalAB.ts — does moving the vault gate onto the scale it was calibrated
 * on change the RIGHT bypass decisions?
 *
 * WHY THIS EXISTS. `VAULT_LEAD_SCORE = 0.70` was set by `dev/source/judge_probe.py`,
 * which embeds the BARE query over the WHOLE index. Production applies it to
 * `mainSearchLead.score`, which comes from `expandQuery(...)` narrowed to the routed
 * SOURCE_SET. S229 measured the offset on the same 24 queries that set the bar and found
 * expansion lifts scores by up to +0.3226 while routing lifts nothing, so two CLASS_B
 * adversarial queries clear 0.70 on the applied scale and skip the judge.
 * `FEATURE_VAULT_GATE_RAWVEC=1` (searchChannelB.ts) reads the same lead chunk's cosine
 * against the bare vector instead. The 0.70 constant is untouched.
 *
 * WHAT THIS MEASURES, AND WHY NOT THE WAY S229 DID IT. `_s229_leadDetail.ts` inferred
 * `mainSearchLead` from the window by taking the maximal descending suffix, because the
 * gate's input is internal. That is an inference and it can be wrong. Here the decision
 * is OBSERVED instead: a stub judge records whether it was consulted at all, so
 * "bypass fired" is a fact about the run rather than a reconstruction of it. The stub
 * returns 能 in both arms, so synthesis proceeds either way and the ONLY observable
 * difference between arms is whether the judge was asked.
 *
 * The gate identifies its own subject for us: with the flag on it reads the lead chunk's
 * embedding by primary key, so intercepting that one URL yields the exact chunk id the
 * gate tested. Its applied-scale score is then read off the returned window by id, and
 * its bare-scale cosine is computed from the same row the gate used. Nothing is inferred.
 *
 * READ-ONLY. No synthesizer model, no judge model, no writes. Two searches per query.
 *
 * USAGE (from backend/)
 *   node_modules/.bin/tsx --env-file=.env scripts/_s230_gateSignalAB.ts --self-test
 *   node_modules/.bin/tsx --env-file=.env scripts/_s230_gateSignalAB.ts <out.json>
 */
import fs from 'node:fs';
import { searchChannelB, detectQueryCategory } from '../src/api/searchChannelB.js';

const SUPABASE_HOST = 'youkcekbrbywuqjxgibe.supabase.co';
const OPENAI_HOST = 'api.openai.com';
process.env.SUPABASE_URL ||= `https://${SUPABASE_HOST}`;
// Measurement key note (handoff Risks 2b): this falls back to the SERVICE key's 8s
// ceiling, not anon's 3s. Scores are unaffected; failure RATES would be optimistic.
process.env.SUPABASE_ANON_KEY ||= process.env.SUPABASE_SERVICE_KEY;
// Production has FEATURE_ROUTE_FIRST_SEARCH=1 (Render env, S220). Both arms must set it
// or the routed path measured here is not the one production runs (`_s226_knobAB.ts:139`).
process.env.FEATURE_ROUTE_FIRST_SEARCH = '1';

const VAULT_BAR = 0.70;

/** The exact case set that set the bar — `dev/source/judge_probe.py` CLASS_A/B/C.
 *  Kept verbatim: this is an acceptance key, not a query list to tune. */
const CASES: ReadonlyArray<{ q: string; klass: 'A' | 'B' | 'C' }> = [
  { q: '香港股票市場今日收市指數', klass: 'A' },
  { q: '米線湯底煮法食譜', klass: 'A' },
  { q: '英超足球聯賽賽程表', klass: 'A' },
  { q: '比特幣今年價格走勢', klass: 'A' },
  { q: '台灣高鐵時刻表同票價', klass: 'A' },
  { q: 'iPhone 換電池保養價錢', klass: 'A' },
  { q: '教師每年可以請幾多日大假', klass: 'B' },
  { q: '校長退休金點樣計', klass: 'B' },
  { q: '解僱教師要俾幾多個月遣散費', klass: 'B' },
  { q: '幼稚園每班最多可以收幾多個學生', klass: 'B' },
  { q: '學校泳池水質檢測標準係咩', klass: 'B' },
  { q: '老師病假連續請幾耐先要交醫生紙', klass: 'B' },
  { q: '學校可唔可以借錢俾教職員', klass: 'B' },
  { q: '校巴司機最低工資係幾多', klass: 'B' },
  { q: '學生喺校內可以用手機幾耐', klass: 'B' },
  { q: '教師評核幾多分先算合格', klass: 'B' },
  { q: '學校每堂補習費可以收幾多', klass: 'B' },
  { q: '校服供應商招標要幾多間報價', klass: 'B' },
  { q: '體罰投訴要幾多日內處理完', klass: 'B' },
  { q: '課室冷氣應該調到幾多度', klass: 'B' },
  { q: '人工智能初探', klass: 'C' },
  { q: '資訊及通訊科技 課程指引', klass: 'C' },
  { q: '跟車保母有咩要求', klass: 'C' },
  { q: '校巴司機安全指引', klass: 'C' },
];

/**
 * S229 opened two of these chunk by chunk and the two verdicts differ, so they are
 * recorded here as the pre-registered expectation rather than decided after the run:
 *   - 校巴司機最低工資係幾多 @ 0.7098 — REAL gap. 31 chunks across four sources in the
 *     window, zero hits for 工資 or 薪; whole index has 10 hits for 最低工資 and all are
 *     economics / liberal-studies curriculum documents. The judge must NOT be skipped.
 *   - 老師病假連續請幾耐先要交醫生紙 @ 0.7003 — probe MISLABEL, not a defect. g04 states
 *     「常額教師如申請病假超逾兩天，必須出示有效的醫生證明書」and the leading chunk IS
 *     that passage, so the bypass firing is correct behaviour and must be KEPT.
 */
const EXPECT_BYPASS_AFTER: Readonly<Record<string, boolean>> = {
  '校巴司機最低工資係幾多': false,
  '老師病假連續請幾耐先要交醫生紙': true,
};

/** The gate's own read-back: one row by primary key, embedding only. */
const GATE_URL_RE = /\/rest\/v1\/wiki_chunks\?id=eq\.([^&]+)&select=embedding/;

export function gateChunkIdFromUrl(url: string): string | undefined {
  const m = GATE_URL_RE.exec(url);
  return m ? decodeURIComponent(m[1]) : undefined;
}

export function cosine(a: number[], b: number[]): number {
  let dot = 0, na = 0, nb = 0;
  const n = Math.min(a.length, b.length);
  for (let i = 0; i < n; i++) { dot += a[i] * b[i]; na += a[i] * a[i]; nb += b[i] * b[i]; }
  return na && nb ? dot / (Math.sqrt(na) * Math.sqrt(nb)) : 0;
}

export type Arm = { bypassed: boolean; judgeCalls: number };

/**
 * Verdict for one case. `klass` carries the intent the bar was set with: a CLASS_B
 * bypass that stops is the point of the change; a CLASS_C bypass that stops is a real
 * loss. Named explicitly so a summary line cannot quietly net them against each other.
 */
export function classify(
  klass: 'A' | 'B' | 'C',
  before: boolean,
  after: boolean,
  expected: boolean | undefined
): string {
  if (expected !== undefined && after !== expected) return 'VIOLATES_PREREGISTERED';
  if (before === after) return 'UNCHANGED';
  if (before && !after) return klass === 'C' ? 'CONTROL_LOST' : 'ADVERSARIAL_GATED';
  return klass === 'C' ? 'CONTROL_GAINED' : 'ADVERSARIAL_OPENED';
}

function selfTest(): number {
  let fails = 0;
  const ok = (name: string, cond: boolean) => {
    if (!cond) { fails++; console.log(`  FAIL ${name}`); } else console.log(`  ok   ${name}`);
  };

  ok('gate url parsed',
    gateChunkIdFromUrl(`https://h/rest/v1/wiki_chunks?id=eq.abc%2F1&select=embedding&limit=1`) === 'abc/1');
  ok('spotlight overlay url is NOT mistaken for the gate read-back',
    gateChunkIdFromUrl(`https://h/rest/v1/wiki_chunks?source_id=in.(a,b)&select=id,hash,text,embedding&limit=600`) === undefined);
  ok('rpc url is not the gate read-back',
    gateChunkIdFromUrl(`https://h/rest/v1/rpc/match_wiki_chunks_routed`) === undefined);

  ok('cosine of a vector with itself is 1', Math.abs(cosine([1, 2, 3], [1, 2, 3]) - 1) < 1e-12);
  ok('cosine ignores magnitude', Math.abs(cosine([1, 0], [7, 0]) - 1) < 1e-12);
  ok('cosine of empty is 0', cosine([], [1]) === 0);

  ok('B losing its bypass is the intended direction', classify('B', true, false, undefined) === 'ADVERSARIAL_GATED');
  ok('C losing its bypass is a control loss', classify('C', true, false, undefined) === 'CONTROL_LOST');
  ok('no change reports UNCHANGED', classify('B', false, false, undefined) === 'UNCHANGED');
  ok('a newly opened bypass is never silent', classify('B', false, true, undefined) === 'ADVERSARIAL_OPENED');

  // RED-TEST ASSERTION — the pre-registered expectation must be able to fail the run.
  // 校巴司機最低工資 is pre-registered as "must lose its bypass"; if a run reported it
  // still bypassing, this classifier has to say so rather than fold it into UNCHANGED.
  ok('pre-registered expectation overrides every other verdict',
    classify('B', true, true, false) === 'VIOLATES_PREREGISTERED' &&
    classify('B', false, false, true) === 'VIOLATES_PREREGISTERED');

  console.log(fails === 0 ? '\nALL PASS' : `\n${fails} FAILED`);
  return fails === 0 ? 0 : 1;
}

if (process.argv.includes('--self-test')) {
  process.exit(selfTest());
}

const nativeFetch = globalThis.fetch;
let gateReads: Array<{ id: string; embedding: number[] }> = [];

globalThis.fetch = async (input: any, init?: any) => {
  const raw = String(typeof input === 'string' ? input : input.url);
  const url = new URL(raw);
  if (url.hostname !== SUPABASE_HOST && url.hostname !== OPENAI_HOST) {
    throw new Error(`Request boundary: ${url.hostname}`);
  }
  const resp = await nativeFetch(input, { ...(init ?? {}), signal: AbortSignal.timeout(30000) });
  const gateId = gateChunkIdFromUrl(raw);
  if (gateId && resp.ok) {
    // Read the body through a clone so the gate still consumes its own response.
    const rows = (await resp.clone().json()) as Array<{ embedding: unknown }>;
    const v = rows.length === 0 ? [] : (typeof rows[0].embedding === 'string'
      ? JSON.parse(rows[0].embedding as string) as number[]
      : (rows[0].embedding as number[]) ?? []);
    gateReads.push({ id: gateId, embedding: v });
  }
  return resp;
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

/** Judge stub: records that it was consulted, then answers 能 so both arms synthesize. */
function makeStubs() {
  let judgeCalls = 0;
  const judgeFn = async (_p: string) => { judgeCalls++; return '能'; };
  const llmFn = async (_p: string) => 'STUB_SYNTHESIS';
  return { judgeFn, llmFn, calls: () => judgeCalls };
}

async function runArm(query: string, rawVecGate: boolean): Promise<Arm & { leadId?: string; leadEmbedding?: number[]; results: any[] }> {
  if (rawVecGate) process.env.FEATURE_VAULT_GATE_RAWVEC = '1';
  else delete process.env.FEATURE_VAULT_GATE_RAWVEC;
  gateReads = [];
  const stubs = makeStubs();
  const resp: any = await searchChannelB({ query, synthesize: true }, embed, stubs.llmFn, stubs.judgeFn);
  const judgeCalls = stubs.calls();
  return {
    bypassed: judgeCalls === 0,
    judgeCalls,
    ...(gateReads.length > 0 ? { leadId: gateReads[0].id, leadEmbedding: gateReads[0].embedding } : {}),
    results: (resp.results ?? []) as any[],
  };
}

const out = process.argv[2];
const rows: any[] = [];

for (const { q, klass } of CASES) {
  const before = await runArm(q, false);
  const after = await runArm(q, true);
  const bareVec = await embed(q);

  // The gate names its own subject: `leadId` is the chunk it read back. Its applied-scale
  // score is that id's score in the returned window; its bare-scale cosine comes from the
  // very row the gate used, so the two numbers describe one chunk on two scales.
  const leadId = after.leadId;
  const appliedRow = leadId ? after.results.find((r) => r.id === leadId) : undefined;
  const appliedScore = appliedRow ? appliedRow.score : null;
  const bareScore = after.leadEmbedding && after.leadEmbedding.length > 0
    ? cosine(bareVec, after.leadEmbedding)
    : null;

  const verdict = classify(klass, before.bypassed, after.bypassed, EXPECT_BYPASS_AFTER[q]);
  rows.push({
    query: q, klass, route: detectQueryCategory(q) ?? null,
    lead_chunk_id: leadId ?? null,
    applied_scale_score: appliedScore, bare_scale_score: bareScore,
    offset: appliedScore !== null && bareScore !== null ? appliedScore - bareScore : null,
    bypass_before: before.bypassed, bypass_after: after.bypassed,
    judge_calls_before: before.judgeCalls, judge_calls_after: after.judgeCalls,
    expected_bypass_after: EXPECT_BYPASS_AFTER[q] ?? null,
    verdict,
  });
  console.log(
    `${klass} ${verdict.padEnd(22)} ${q}\n` +
    `    lead ${leadId ?? '(not a vault_extract lead)'}` +
    `  applied ${appliedScore === null ? '  -   ' : appliedScore.toFixed(4)}` +
    `  bare ${bareScore === null ? '  -   ' : bareScore.toFixed(4)}` +
    `  bypass ${before.bypassed ? 'YES' : 'no'} -> ${after.bypassed ? 'YES' : 'no'}`
  );
}

const summary = {
  bar: VAULT_BAR,
  cases: rows.length,
  bypass_before: rows.filter((r) => r.bypass_before).length,
  bypass_after: rows.filter((r) => r.bypass_after).length,
  adversarial_gated: rows.filter((r) => r.verdict === 'ADVERSARIAL_GATED').length,
  adversarial_opened: rows.filter((r) => r.verdict === 'ADVERSARIAL_OPENED').length,
  control_lost: rows.filter((r) => r.verdict === 'CONTROL_LOST').length,
  control_gained: rows.filter((r) => r.verdict === 'CONTROL_GAINED').length,
  violates_preregistered: rows.filter((r) => r.verdict === 'VIOLATES_PREREGISTERED').length,
  unchanged: rows.filter((r) => r.verdict === 'UNCHANGED').length,
};
console.log('\n' + JSON.stringify(summary, null, 2));

if (out) {
  fs.writeFileSync(out, JSON.stringify({ summary, rows }, null, 2));
  console.log(`\nwrote ${out}`);
}
