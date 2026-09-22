/**
 * _s230_judgeTakeover.ts — when the candidate gate takes the bypass away, does the user
 * still get an answer?
 *
 * WHY THIS EXISTS. `_s230_bypassCensus.ts` measured that 59 of 185 gold queries skip the
 * judge today, that 5 of those are FALSE_BYPASS (gold says the corpus cannot answer), and
 * that `FEATURE_VAULT_GATE_RAWVEC=1` blocks 51 of the 59 — all 5 of the false ones, but
 * also 7 of the 10 SOUND ones. Whether that trade is a net gain depends entirely on what
 * the judge does with the queries it is handed, and every earlier probe in this line used
 * a STUB judge precisely so it would measure the gate and nothing else. This one runs the
 * REAL judge on the real window, and it is the only probe in the line that spends model
 * calls.
 *
 * EXTERNAL MODEL BUDGET. Leonard approved this exact batch on 2026-09-22: OpenAI, the
 * production judge model (`getJudgeModel()`), at most 59 calls, stub synthesiser so no
 * answer-model calls. The cap is enforced mechanically below — the counter throws rather
 * than trusting the operator to stop.
 *
 * READING IT. Pre-registered in dev/SESSION_HANDOFF.md `## Validation / QC` S230 batch 6
 * BEFORE this ran: ship support needs >=4 of 5 FALSE_BYPASS to become declines AND >=6 of
 * the 7 blocked SOUND to still be answered; >=2 SOUND declines or >=2 FALSE_BYPASS still
 * answered means do not ship; the 44 WRONG_PASSAGE are reported but are not ship evidence,
 * and >=30 of them declining must be reported as a decline-rate warning on its own.
 *
 * A TECHNICAL FAILURE IS NOT A VERDICT. `judgeCanAnswer()` returns true when the call
 * throws (fail-open to answering), so one failure looks exactly like one 能. The raw reply
 * and any exception are recorded per row and errors are excluded from the verdict counts —
 * the same silent trap S198 recorded.
 *
 * USAGE (from backend/)
 *   node_modules/.bin/tsx --env-file=.env scripts/_s230_judgeTakeover.ts --self-test
 *   node_modules/.bin/tsx --env-file=.env scripts/_s230_judgeTakeover.ts --run --approved-max-calls=59 <out.json>
 */
import fs from 'node:fs';
import { searchChannelB } from '../src/api/searchChannelB.js';

const SUPABASE_HOST = 'youkcekbrbywuqjxgibe.supabase.co';
const OPENAI_HOST = 'api.openai.com';
process.env.SUPABASE_URL ||= `https://${SUPABASE_HOST}`;
process.env.SUPABASE_ANON_KEY ||= process.env.SUPABASE_SERVICE_KEY;
process.env.FEATURE_ROUTE_FIRST_SEARCH = '1';

const APPROVED_CAP = 59;
/** The stub answer model returns exactly this, so "the synthesiser ran" is decidable without
 *  knowing the decline text. Matching on `SYNTHESIS_DECLINE` instead was the first draft and
 *  it was wrong: that constant is a long paragraph, not 「找不到相關政策。」(which only covers an
 *  empty window), so every decline would have been counted as an answer. Keying on the marker
 *  is also drift-proof — it stays correct if the decline wording is ever rewritten. */
const STUB_ANSWER = 'STUB_SYNTHESIS';

export type Outcome = 'KEEPS_BYPASS' | 'JUDGE_ANSWERS' | 'JUDGE_DECLINES' | 'JUDGE_ERROR';

/**
 * The outcome of one query under the candidate. `judgeCalls === 0` means the gate never
 * blocked, so nothing changed for that query. An error is its own outcome and never a
 * verdict, because the production fail-open would have answered on it.
 */
export function outcomeOf(judgeCalls: number, judgeError: string | null, synthesis: string | undefined): Outcome {
  if (judgeCalls === 0) return 'KEEPS_BYPASS';
  if (judgeError) return 'JUDGE_ERROR';
  return synthesis === STUB_ANSWER ? 'JUDGE_ANSWERS' : 'JUDGE_DECLINES';
}

/** Records what the response actually looked like, so an unexpected third shape cannot hide
 *  inside the decline count. */
export function synthesisShape(synthesis: string | undefined): 'stub' | 'decline' | 'empty' | 'other' {
  if (synthesis === undefined || synthesis === '') return 'empty';
  if (synthesis === STUB_ANSWER) return 'stub';
  if (synthesis.startsWith('根據檢索到的教育局文件') || synthesis.startsWith('找不到相關政策')) return 'decline';
  return 'other';
}

/** The production judge reads only the first character: 能 answers, anything else declines. */
export function verdictOf(raw: string): '能' | '否' | 'unparsed' {
  const t = raw.trim();
  if (t.startsWith('能')) return '能';
  if (t.startsWith('否')) return '否';
  return 'unparsed';
}

function selfTest(): number {
  let fails = 0;
  const ok = (n: string, c: boolean) => { if (!c) { fails++; console.log(`  FAIL ${n}`); } else console.log(`  ok   ${n}`); };

  ok('no judge call means the bypass survived', outcomeOf(0, null, 'X') === 'KEEPS_BYPASS');
  ok('only the stub marker counts as an answer', outcomeOf(1, null, 'STUB_SYNTHESIS') === 'JUDGE_ANSWERS');
  ok('the real decline paragraph is a decline',
    outcomeOf(1, null, '根據檢索到的教育局文件，暫時未能找到可直接回答此問題的明確資料。') === 'JUDGE_DECLINES');
  // RED-TEST ASSERTION — the first draft matched on 「找不到相關政策。」, which is only the
  // empty-window text, and would have scored every real decline as an answer. Anything that
  // is not the stub marker must count as "no answer reached the user".
  ok('the short empty-window text is not mistaken for an answer',
    outcomeOf(1, null, '找不到相關政策。') === 'JUDGE_DECLINES');
  ok('an unexpected shape is visible, not silently a decline', synthesisShape('something else') === 'other');
  ok('the real decline paragraph is recognised', synthesisShape('根據檢索到的教育局文件，暫時未能') === 'decline');
  // RED-TEST ASSERTION — production fails open, so an error would otherwise be counted as
  // a 能. If this ever reports JUDGE_ANSWERS the run can no longer tell a verdict from an
  // outage, which is the S198 trap this line of work has already paid for once.
  ok('an error is never counted as an answer', outcomeOf(1, 'HTTP 429', 'STUB_SYNTHESIS') === 'JUDGE_ERROR');
  ok('error outranks a decline too', outcomeOf(1, 'boom', '根據檢索到的教育局文件') === 'JUDGE_ERROR');

  ok('能 parsed', verdictOf('能，第 2 段有答案') === '能');
  ok('否 parsed', verdictOf('否') === '否');
  ok('noise is unparsed, not an answer', verdictOf('I think so') === 'unparsed');

  console.log(fails === 0 ? '\nALL PASS' : `\n${fails} FAILED`);
  return fails === 0 ? 0 : 1;
}

if (process.argv.includes('--self-test')) process.exit(selfTest());

const approvedArg = process.argv.find((a) => a.startsWith('--approved-max-calls='));
const approved = Number(approvedArg?.slice('--approved-max-calls='.length));
if (!process.argv.includes('--run') || !Number.isInteger(approved) || approved < 1 || approved > APPROVED_CAP) {
  throw new Error(
    `External model batch: pass --run --approved-max-calls=N with 1 <= N <= ${APPROVED_CAP}. ` +
    `Leonard approved at most ${APPROVED_CAP} judge calls on 2026-09-22; anything beyond that needs a new approval.`
  );
}

const nativeFetch = globalThis.fetch;
globalThis.fetch = async (input: any, init?: any) => {
  const url = new URL(String(typeof input === 'string' ? input : input.url));
  if (url.hostname !== SUPABASE_HOST && url.hostname !== OPENAI_HOST) {
    throw new Error(`Request boundary: ${url.hostname}`);
  }
  return nativeFetch(input, { ...(init ?? {}), signal: AbortSignal.timeout(60000) });
};

async function embed(text: string): Promise<number[]> {
  const r = await nativeFetch('https://api.openai.com/v1/embeddings', {
    method: 'POST',
    headers: { Authorization: `Bearer ${process.env.OPENAI_API_KEY}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ model: 'text-embedding-3-small', input: text }),
    signal: AbortSignal.timeout(30000),
  });
  if (!r.ok) throw new Error(`Embedding HTTP ${r.status}`);
  return ((await r.json()) as any).data[0].embedding as number[];
}

const { createLlmClient } = await import('../src/lib/llmClient.js');
const { getJudgeModel } = await import('../src/config/env.js');
const judgeModel = getJudgeModel();
const judge = createLlmClient({ model: judgeModel, maxRetries: 0 });

let spent = 0;
function spend(): void {
  spent++;
  if (spent > approved) throw new Error(`Approved budget exhausted at ${approved} judge calls`);
}

const census = JSON.parse(
  fs.readFileSync('../dev/source/eval_runs/2026-09-22_s230_bypass_census.json', 'utf8')
) as { rows: Array<Record<string, any>> };
const targets = census.rows.filter((r) => r.bypass_before);
console.log(`judge model ${judgeModel} · ${targets.length} bypassing queries · budget ${approved}\n`);

process.env.FEATURE_VAULT_GATE_RAWVEC = '1';
const rows: any[] = [];

for (let i = 0; i < targets.length; i++) {
  const t = targets[i];
  let judgeCalls = 0;
  let raw = '';
  let judgeError: string | null = null;

  const judgeFn = async (prompt: string): Promise<string> => {
    judgeCalls++;
    spend();
    try {
      raw = await judge(prompt);
      return raw;
    } catch (e) {
      judgeError = String(e).slice(0, 200);
      throw e; // let production's own fail-open path run, so the outcome is the real one
    }
  };
  const llmFn = async (_p: string) => STUB_ANSWER;

  let synthesis: string | undefined;
  let searchError: string | null = null;
  try {
    const resp: any = await searchChannelB({ query: t.query, synthesize: true }, embed, llmFn, judgeFn);
    synthesis = resp.synthesis;
  } catch (e) {
    searchError = String(e).slice(0, 200);
  }

  const outcome = searchError ? 'JUDGE_ERROR' : outcomeOf(judgeCalls, judgeError, synthesis);
  rows.push({
    id: t.id, query: t.query, gold_verdict: t.bypass_verdict, answerable: t.answerable,
    applied_scale_score: t.applied_scale_score, bare_scale_score: t.bare_scale_score,
    judge_calls: judgeCalls, judge_raw: raw.slice(0, 200) || null,
    judge_verdict: raw ? verdictOf(raw) : null,
    judge_error: judgeError, search_error: searchError,
    synthesis_shape: synthesisShape(synthesis),
    outcome,
  });
  console.log(
    `[${i + 1}/${targets.length}] ${String(t.bypass_verdict).padEnd(13)} ${outcome.padEnd(14)}` +
    ` ${raw ? verdictOf(raw) : '-'}  ${String(t.query).slice(0, 40)}`
  );
  // Pace the batch: the handoff records gpt-4.1 aborting a run at its 30k TPM ceiling, and
  // a windowed judge prompt is a few thousand tokens.
  await new Promise((r) => setTimeout(r, 1200));
}

const by = (v: string) => rows.filter((r) => r.gold_verdict === v);
function tally(v: string) {
  const g = by(v);
  return {
    n: g.length,
    KEEPS_BYPASS: g.filter((r) => r.outcome === 'KEEPS_BYPASS').length,
    JUDGE_ANSWERS: g.filter((r) => r.outcome === 'JUDGE_ANSWERS').length,
    JUDGE_DECLINES: g.filter((r) => r.outcome === 'JUDGE_DECLINES').length,
    JUDGE_ERROR: g.filter((r) => r.outcome === 'JUDGE_ERROR').length,
  };
}

const summary = {
  judge_model: judgeModel,
  approved_calls: approved,
  judge_calls_spent: spent,
  queries: rows.length,
  errors: rows.filter((r) => r.outcome === 'JUDGE_ERROR').length,
  unparsed_verdicts: rows.filter((r) => r.judge_verdict === 'unparsed').length,
  unexpected_synthesis_shapes: rows.filter((r) => r.synthesis_shape === 'other').length,
  FALSE_BYPASS: tally('FALSE_BYPASS'),
  SOUND: tally('SOUND'),
  WRONG_PASSAGE: tally('WRONG_PASSAGE'),
};
console.log('\n' + JSON.stringify(summary, null, 2));

const out = process.argv.find((a) => a.endsWith('.json') && !a.startsWith('--'));
if (out) {
  fs.writeFileSync(out, JSON.stringify({ summary, rows }, null, 2));
  console.log(`\nwrote ${out}`);
}
