/**
 * _s230_leadOverlap.ts — the real gap and the legitimate bypasses fail differently.
 * Does word presence separate them where cosine cannot?
 *
 * WHY. `_s230_gateSignalAB.ts` measured that moving the vault bar onto its calibration
 * scale removes every bypass (5 -> 0), including 人工智能初探 and 資訊及通訊科技 課程指引 —
 * and the frozen judge acceptance set (dev/source/judge_acceptance_cases.json, runs
 * 2026-08-02_s202_v4b_frozen35{,_r2,_r3}.json) records the judge answering 否 on both of
 * those THREE times although both are `want: 能`. So the judge cannot take over from the
 * bypass for title-like queries, which is what S183 built the bypass for.
 *
 * The one real gap failed a different way: S229 opened 校巴司機最低工資係幾多 chunk by
 * chunk and found zero hits for 工資 or 薪 across the 31 chunks of the window. That is a
 * LEXICAL absence, not a cosine deficit — the same shape S196 already gated on the
 * footnote lead slot (FOOTNOTE_LEAD_MIN_OVERLAP), where the same reasoning is recorded.
 *
 * This script only MEASURES the separation, using the informative-bigram machinery the
 * footnote gate already uses. It changes no behaviour and proposes no constant: the point
 * is to see whether the two populations separate at all before anyone designs a gate.
 *
 * READ-ONLY. No embeddings, no LLM: it reads the lead chunks named by the A/B artifact.
 *
 * --window re-runs each search and applies the same measure to the WHOLE synthesis
 * window instead of the lead chunk alone, because S229's observation was window-wide
 * (zero hits for 工資 or 薪 across all 31 chunks) and a single chunk can legitimately
 * lack the query's words while its neighbours carry the answer.
 *
 * USAGE (from backend/)
 *   node_modules/.bin/tsx --env-file=.env scripts/_s230_leadOverlap.ts <ab_artifact.json>
 *   node_modules/.bin/tsx --env-file=.env scripts/_s230_leadOverlap.ts <ab_artifact.json> --window --out <o.json>
 */
import fs from 'node:fs';
import { overlapWith, queryInformativeBigrams } from '../src/lib/textBigrams.js';
import { footnoteInformativeBigrams } from '../src/lib/wikiRepository.js';
import { searchChannelB } from '../src/api/searchChannelB.js';

const SUPABASE_HOST = 'youkcekbrbywuqjxgibe.supabase.co';
process.env.SUPABASE_URL ||= `https://${SUPABASE_HOST}`;
process.env.SUPABASE_ANON_KEY ||= process.env.SUPABASE_SERVICE_KEY;

// Production configuration, both measures (handoff: FEATURE_ROUTE_FIRST_SEARCH=1).
process.env.FEATURE_ROUTE_FIRST_SEARCH = '1';
const windowMode = process.argv.includes('--window');

async function embed(text: string): Promise<number[]> {
  const r = await fetch('https://api.openai.com/v1/embeddings', {
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

/** The synthesis window is `results.slice(0, 5)` (searchChannelB.ts defaultWindow). */
async function windowText(query: string): Promise<string> {
  const resp: any = await searchChannelB({ query, synthesize: false }, embed);
  return ((resp.results ?? []) as any[]).slice(0, 5).map((r) => r.text).join('\n');
}

const artifact = process.argv[2];
if (!artifact) throw new Error('need the _s230_gateSignalAB artifact path');
const { rows } = JSON.parse(fs.readFileSync(artifact, 'utf8')) as {
  rows: Array<{
    query: string; klass: string; lead_chunk_id: string | null;
    applied_scale_score: number | null; bare_scale_score: number | null;
    bypass_before: boolean; verdict: string;
  }>;
};

const key = process.env.SUPABASE_SERVICE_KEY!;
async function chunkText(id: string): Promise<string> {
  const url = `https://${SUPABASE_HOST}/rest/v1/wiki_chunks?id=eq.${encodeURIComponent(id)}&select=text&limit=1`;
  const r = await fetch(url, { headers: { apikey: key, Authorization: `Bearer ${key}` } });
  if (!r.ok) throw new Error(`chunk text ${r.status}`);
  const j = (await r.json()) as Array<{ text: string }>;
  return j.length ? j[0].text : '';
}

const stop = await footnoteInformativeBigrams();
const out: any[] = [];

for (const row of rows) {
  if (!row.lead_chunk_id) continue;
  const text = windowMode ? await windowText(row.query) : await chunkText(row.lead_chunk_id);
  const bigrams = queryInformativeBigrams(row.query, stop);
  const overlap = overlapWith(bigrams, text);
  out.push({
    query: row.query, klass: row.klass, bypass_before: row.bypass_before,
    verdict: row.verdict,
    applied: row.applied_scale_score, bare: row.bare_scale_score,
    query_bigrams: bigrams.size, overlap,
    overlap_fraction: bigrams.size ? overlap / bigrams.size : null,
  });
}

out.sort((a, b) => (a.overlap_fraction ?? -1) - (b.overlap_fraction ?? -1));
for (const r of out) {
  const mark = r.bypass_before ? (r.verdict === 'ADVERSARIAL_GATED' ? 'REAL-GAP ' : 'BYPASS   ') : '         ';
  console.log(
    `${r.klass} ${mark} overlap ${String(r.overlap).padStart(2)}/${String(r.query_bigrams).padEnd(2)}` +
    ` = ${(r.overlap_fraction ?? 0).toFixed(2)}  applied ${(r.applied ?? 0).toFixed(4)} bare ${(r.bare ?? 0).toFixed(4)}  ${r.query}`
  );
}

const bypassed = out.filter((r) => r.bypass_before);
const realGap = bypassed.filter((r) => r.verdict === 'ADVERSARIAL_GATED');
const legit = bypassed.filter((r) => r.verdict !== 'ADVERSARIAL_GATED');
// `separates` is deliberately computed over judgeable cases ONLY, and the count of
// unjudgeable ones is reported beside it. A query with no informative bigrams (人工智能初探
// has none) gives this measure nothing, and textBigrams.ts states the rule explicitly:
// "cannot judge" must never be read as "no overlap". Folding those into a 0 would make any
// gate built on this refuse exactly the title-like queries the bypass exists for.
const judgeableLegit = legit.filter((r) => r.overlap_fraction !== null);
const summary = {
  measure: windowMode ? 'whole synthesis window (top 5)' : 'lead chunk only',
  bypassed_before: bypassed.length,
  real_gap_overlap: realGap.map((r) => r.overlap_fraction),
  legitimate_overlap: legit.map((r) => r.overlap_fraction),
  unjudgeable_legitimate: legit.length - judgeableLegit.length,
  separates_among_judgeable: realGap.length > 0 && judgeableLegit.length > 0
    ? Math.max(...realGap.map((r) => r.overlap_fraction ?? 0)) < Math.min(...judgeableLegit.map((r) => r.overlap_fraction ?? 0))
    : null,
};
console.log('\n' + JSON.stringify(summary, null, 2));

const outIdx = process.argv.indexOf('--out');
if (outIdx > 0 && process.argv[outIdx + 1]) {
  fs.writeFileSync(process.argv[outIdx + 1], JSON.stringify({ summary, rows: out }, null, 2));
  console.log(`\nwrote ${process.argv[outIdx + 1]}`);
}
