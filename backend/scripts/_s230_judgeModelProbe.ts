/**
 * _s230_judgeModelProbe.ts — is the one remaining SOUND decline a PROMPT problem or a MODEL
 * problem?
 *
 * WHY. Under the tightened candidate the only sound bypass that turns into a decline is
 * 「家長校董 點選」: slot 0 of its window is a curated footnote whose text IS the gold passage
 * signature, and the production judge still answered 否. Before touching the judge prompt it
 * is worth knowing whether the prompt is at fault at all — S211 already recorded that five
 * prompt rewrites plus gpt-4o could not fix a case of this shape, while the handoff records
 * for the OTHER judge in this codebase that "mini 是壞尺" and requires gpt-4.1. The relevance
 * judge's acceptance run (S201) was made on gpt-4o-mini; production now runs gpt-4.1-mini.
 * Those are different models, and nobody has checked whether the model is the lever.
 *
 * METHOD. Capture the EXACT prompt production builds — same window, same RELEVANCE_JUDGE_PROMPT
 * — by letting `searchChannelB` run with a judge stub that records its argument and answers 能
 * (so nothing downstream changes). Then send that captured prompt to each model in turn. No
 * prompt is rewritten and no window is reconstructed, so a difference can only be the model.
 *
 * DELIBERATELY TINY. This is a diagnostic, not an acceptance run: 3 queries x 2 models = at
 * most 6 completions, capped in code. Accepting a judge change needs the frozen 35-case set
 * (dev/source/judge_acceptance.py) per DOC_SYNC_CHECKLIST row 46, which is a separate,
 * separately approved batch.
 *
 * USAGE (from backend/)
 *   node_modules/.bin/tsx --env-file=.env scripts/_s230_judgeModelProbe.ts --run
 */
import { searchChannelB } from '../src/api/searchChannelB.js';

const SUPABASE_HOST = 'youkcekbrbywuqjxgibe.supabase.co';
process.env.SUPABASE_URL ||= `https://${SUPABASE_HOST}`;
process.env.SUPABASE_ANON_KEY ||= process.env.SUPABASE_SERVICE_KEY;
process.env.FEATURE_ROUTE_FIRST_SEARCH = '1';

const MAX_COMPLETIONS = 6;

/** The failing case, plus two controls from the frozen acceptance set: one the judge is
 *  recorded as getting right (answer half) and one it must keep declining (decline half). */
const CASES: ReadonlyArray<{ query: string; want: '能' | '否'; why: string }> = [
  { query: '家長校董 點選', want: '能',
    why: 'the one SOUND decline; slot 0 is the curated footnote that IS the gold signature' },
  { query: '人工智能初探', want: '能',
    why: 'S01_ai_intro_bare_noun — answer half, and the judge is recorded saying 否 three times' },
  { query: '學生請病假要唔要交醫生紙', want: '否',
    why: 'D01_student_sickleave — must stay declined; every chunk is STAFF sick leave (S201)' },
];

const MODELS = ['gpt-4.1-mini', 'gpt-4.1'] as const;

if (!process.argv.includes('--run')) {
  throw new Error(`Diagnostic batch: pass --run. At most ${MAX_COMPLETIONS} judge completions ` +
    `(${CASES.length} queries x ${MODELS.length} models). Accepting a judge change needs the ` +
    `frozen 35-case set per DOC_SYNC_CHECKLIST row 46, which is a separate approved batch.`);
}

const nativeFetch = globalThis.fetch;
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
let spent = 0;

for (const c of CASES) {
  // Capture production's own prompt: the stub answers 能 so the rest of the pipeline is
  // untouched. FEATURE_VAULT_GATE_RAWVEC must be SET — the first version left it unset and
  // two of the three cases never reached the judge at all, because on the production path
  // their applied score clears 0.70 and the bypass fires. The candidate is precisely the
  // configuration in which these queries DO reach the judge, so that is what to capture.
  process.env.FEATURE_VAULT_GATE_RAWVEC = '1';
  let captured = '';
  const judgeFn = async (prompt: string) => { captured = prompt; return '能'; };
  const llmFn = async (_p: string) => 'STUB';
  await searchChannelB({ query: c.query, synthesize: true }, embed, llmFn, judgeFn);
  if (!captured) {
    console.log(`\n${c.query} — judge was never consulted (bypass fired); nothing to compare.`);
    continue;
  }

  console.log(`\n=== ${c.query}   want ${c.want}\n    ${c.why}`);
  for (const model of MODELS) {
    if (spent >= MAX_COMPLETIONS) throw new Error('diagnostic cap reached');
    spent++;
    const judge = createLlmClient({ model, maxRetries: 0 });
    let verdict: string;
    try {
      verdict = (await judge(captured)).trim().slice(0, 12);
    } catch (e) {
      verdict = `ERROR ${String(e).slice(0, 60)}`;
    }
    const mark = verdict.startsWith(c.want) ? 'correct' : 'WRONG';
    console.log(`    ${model.padEnd(14)} → ${verdict.padEnd(14)} ${mark}`);
  }
}
console.log(`\ncompletions spent: ${spent} / cap ${MAX_COMPLETIONS}`);
