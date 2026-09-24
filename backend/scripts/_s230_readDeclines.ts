/**
 * _s230_readDeclines.ts — print the synthesis window for the queries the candidate turns
 * from answered into declined, so a human can say whether each decline is a loss or a
 * correct abstention.
 *
 * WHY. `_s230_judgeTakeover.ts` measured ten WRONG_PASSAGE queries flipping from answered
 * to declined under `FEATURE_VAULT_GATE_RAWVEC=1`. Gold calls all ten answerable, but none
 * has an expected passage signature in the window, so the judge's decline may well be the
 * correct behaviour rather than a lost answer. That question cannot be settled by a score:
 * it needs the window read. This prints exactly what the judge saw — the five chunks, the
 * gold expectation, and the signatures it was looking for.
 *
 * It also prints the two queries the candidate NEWLY sends through the bypass, for the same
 * reason: whether skipping the judge there is safe depends on what is in the window.
 *
 * READ-ONLY, synthesize:false — no judge and no answer model.
 *
 * USAGE (from backend/)
 *   node_modules/.bin/tsx --env-file=.env scripts/_s230_readDeclines.ts [--chars N]
 */
import fs from 'node:fs';
import { searchChannelB } from '../src/api/searchChannelB.js';

const SUPABASE_HOST = 'youkcekbrbywuqjxgibe.supabase.co';
process.env.SUPABASE_URL ||= `https://${SUPABASE_HOST}`;
process.env.SUPABASE_ANON_KEY ||= process.env.SUPABASE_SERVICE_KEY;
process.env.FEATURE_ROUTE_FIRST_SEARCH = '1';

const charsArg = process.argv.indexOf('--chars');
const CHARS = charsArg > 0 ? Number(process.argv[charsArg + 1]) : 260;

async function embed(text: string): Promise<number[]> {
  const r = await fetch('https://api.openai.com/v1/embeddings', {
    method: 'POST',
    headers: { Authorization: `Bearer ${process.env.OPENAI_API_KEY}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ model: 'text-embedding-3-small', input: text }),
    signal: AbortSignal.timeout(30000),
  });
  if (!r.ok) throw new Error(`Embedding HTTP ${r.status}`);
  return ((await r.json()) as any).data[0].embedding as number[];
}

const takeover = JSON.parse(fs.readFileSync('../dev/source/eval_runs/2026-09-22_s230_judge_takeover.json', 'utf8'));
const census = JSON.parse(fs.readFileSync('../dev/source/eval_runs/2026-09-22_s230_bypass_census.json', 'utf8'));
const gold = JSON.parse(fs.readFileSync('../dev/_s213_gold_all.json', 'utf8')) as Array<Record<string, any>>;
const goldById = new Map(gold.map((g) => [g.id, g]));

const declines = takeover.rows.filter((r: any) => r.outcome === 'JUDGE_DECLINES');
const newBypass = census.rows.filter((r: any) => r.bypass_after && !r.bypass_before);

async function show(label: string, id: string, query: string, extra: string) {
  const g = goldById.get(id) ?? {};
  const resp: any = await searchChannelB({ query, synthesize: false }, embed);
  const rs = (resp.results ?? []) as any[];
  console.log(`\n${'='.repeat(100)}\n${label}  ${id}\n查詢：${query}\n${extra}`);
  console.log(`gold intent：${String(g.intent ?? '-').slice(0, 200)}`);
  console.log(`gold expected_source_any：${JSON.stringify(g.expected_source_any ?? [], null, 0)}`);
  console.log(`gold expected_passage_signature：${JSON.stringify(g.expected_passage_signature ?? [], null, 0)}`);
  console.log(`--- 判官看到的窗（top 5）---`);
  rs.slice(0, 5).forEach((r, i) => {
    const sigHit = (g.expected_passage_signature ?? []).some((s: string) => String(r.text).includes(s));
    console.log(
      `  [${i}] ${r.score.toFixed(4)} ${String(r.content_type).padEnd(17)} ${String(r.source_id).padEnd(26)}` +
      `${(g.expected_source_any ?? []).includes(r.source_id) ? ' ★expected-source' : ''}${sigHit ? ' ★signature' : ''}\n` +
      `      ${String(r.text).replace(/\s+/g, ' ').slice(0, CHARS)}`
    );
  });
}

console.log(`### 十條會由「有答案」變「拒答」的查詢 —— 逐條讀窗判斷是損失還是正確棄權`);
for (const d of declines) {
  await show('DECLINE', d.id, d.query, `applied ${d.applied_scale_score} → bare ${d.bare_scale_score}｜判官：${d.judge_verdict}`);
}
console.log(`\n\n### 兩條候選會【新開】bypass 的查詢 —— 跳過判官是否安全`);
for (const b of newBypass) {
  await show('NEW-BYPASS', b.id, b.query, `applied ${b.applied_scale_score} → bare ${b.bare_scale_score}（裸尺反而更高）`);
}
