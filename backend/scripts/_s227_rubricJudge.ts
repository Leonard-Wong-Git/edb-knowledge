/**
 * _s227_rubricJudge.ts — pairwise rubric judge over two answer texts for the same query.
 *
 * WHY THIS EXISTS (Open Priorities ①). S226 measured a retrieval knob
 * (`FEATURE_LEXICAL_RERANK`) as improving BOTH retrieval layers, then read seven
 * answer pairs by hand and found the answer layer mixed — one clear regression
 * (`hr_maternity` contradicts itself), one honest abstention turned into an
 * off-topic answer (`cpd_conduct_registration`), one number muddled
 * (`dig_teacher_digital_cpd_hours`). The ship decision is blocked on an answer-layer
 * yardstick that scales past seven hand-read pairs. This is that yardstick.
 *
 * WHAT IT IS NOT. It does not retrieve, embed, or touch Supabase. It replays a saved
 * `_s226_knobAB.ts --synthesize` JSONL and asks a judge model to compare the two answer
 * texts already recorded there. Its only network operation is the judge call.
 *
 * THREE PROPERTIES THIS PROJECT HAS ALREADY PAID FOR, BUILT IN HERE:
 *
 * 1. POSITION BIAS IS CONTROLLED. A pairwise judge favours whichever answer it sees
 *    first. Every item is judged TWICE with the sides swapped; agreement across both
 *    orders is required before a winner is recorded. Disagreement records
 *    `INCONSISTENT` — the judge could not tell these apart, which is a finding, not a
 *    tie to be averaged away.
 *
 * 2. THE JUDGE IS CALIBRATED BEFORE IT IS TRUSTED. S226's lesson was "a broken ruler
 *    produced the conclusion that happened to favour me". `--calibration` runs only the
 *    seven pairs a human already read, whose direction is recorded in
 *    `dev/SESSION_HANDOFF.md` (Validation / QC, S226 batch seven), and reports agreement
 *    against them. Low agreement means this tool is unfit for ② — it does not mean
 *    retune the prompt until the judge agrees with me.
 *
 * 3. THE JUDGE CANNOT SEE WHICH SIDE IS WHICH. The prompt says ANSWER 1 / ANSWER 2 and
 *    carries no knob name, no side label, and no evidence window. The evidence windows
 *    differ between sides, so feeding them would leak the side; and the source layer
 *    (expected / forbidden source ids) is already scored by `_s219_score_before_after.py`
 *    and `_s214_run_synthesis_eval.py`. One rule, one place: this judge scores the
 *    answer TEXT against the gold passage, nothing else.
 *
 * SPEND GATE (S214 convention, kept identical): `--approved-max-calls=N` is mandatory and
 * checked BEFORE any client is constructed; `maxRetries: 0` so the SDK cannot silently
 * multiply attempts; the counter is incremented and written to the artifact BEFORE each
 * attempt, so an aborted run still shows what it spent. Leonard approves the batch.
 *
 * USAGE (from backend/)
 *   node_modules/.bin/tsx scripts/_s227_rubricJudge.ts --self-test
 *   node_modules/.bin/tsx --env-file=.env scripts/_s227_rubricJudge.ts \
 *       --run ../dev/source/eval_runs/2026-09-15_s226synth_before_after.jsonl \
 *       --calibration --approved-max-calls=14 --label s227cal
 *   node_modules/.bin/tsx --env-file=.env scripts/_s227_rubricJudge.ts \
 *       --run ../dev/source/eval_runs/2026-09-15_s226synth_before_after.jsonl \
 *       --approved-max-calls=100 --label s227full
 */
import { createHash } from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';

// The exact decline string the synthesiser emits. Copied from
// `dev/_s214_run_synthesis_eval.py` (DECLINE) — if these two ever drift apart, the
// "both sides abstained" shortcut stops firing and every abstention pair costs two
// judge calls instead of zero, which is visible in the artifact rather than silent.
const DECLINE =
  '根據檢索到的教育局文件，暫時未能找到可直接回答此問題的明確資料。'
  + '下方為主題相關的原始文件，或可參考；亦可嘗試以其他關鍵詞重新搜尋。';

// Direction a human recorded for these seven pairs in dev/SESSION_HANDOFF.md
// (## Validation / QC, S226 batch seven). BEFORE = the shipped configuration read
// better; AFTER = the knob side read better. This table is the judge's ground truth,
// so it is transcribed here verbatim in intent and must not be edited to make a run
// pass — editing it is editing the answer key.
const CALIBRATION: Record<string, 'BEFORE' | 'AFTER'> = {
  hr_maternity: 'BEFORE',                 // after contradicts itself on the 14-week figure
  dig_teacher_digital_cpd_hours: 'BEFORE', // "不少於 30 小時" muddled into "30 至 150 小時"
  cpd_conduct_registration: 'BEFORE',      // honest abstention became an off-topic answer
  staff_grad_ratio: 'AFTER',               // after adds the rank breakdown
  fin_ac_grant: 'AFTER',                   // after adds $42,526 and a worked example
  bus_escort_list: 'AFTER',                // after drops only peripheral numbers
  hr_jobshare: 'AFTER',                    // same: closer to the question asked
};

export type Side = 'BEFORE' | 'AFTER';
export type RawVerdict = 'ANSWER_1' | 'ANSWER_2' | 'TIE';
export type Combined =
  | 'BEFORE' | 'AFTER' | 'TIE'
  | 'WEAK_BEFORE' | 'WEAK_AFTER'
  | 'INCONSISTENT'
  | 'TIE_IDENTICAL' | 'TIE_BOTH_DECLINED';

export interface GoldItem {
  id: string;
  query: string;
  intent?: string;
  answerable?: boolean;
  expected_passage_signature?: string[];
  domain?: string;
}

/** Map a raw verdict back to a side, given which side was shown first. */
export function resolveSide(raw: RawVerdict, firstShown: Side): Side | 'TIE' {
  if (raw === 'TIE') return 'TIE';
  const second: Side = firstShown === 'BEFORE' ? 'AFTER' : 'BEFORE';
  return raw === 'ANSWER_1' ? firstShown : second;
}

/**
 * Combine the two orderings. Agreement is required for a plain winner; a winner in one
 * order and a tie in the other is recorded as WEAK_<side> so it is never counted as the
 * same strength of evidence; opposite winners are INCONSISTENT.
 */
export function combine(a: Side | 'TIE', b: Side | 'TIE'): Combined {
  if (a === b) return a === 'TIE' ? 'TIE' : a;
  if (a === 'TIE') return b === 'BEFORE' ? 'WEAK_BEFORE' : 'WEAK_AFTER';
  if (b === 'TIE') return a === 'BEFORE' ? 'WEAK_BEFORE' : 'WEAK_AFTER';
  return 'INCONSISTENT';
}

/**
 * Judge health, measured from the run itself rather than by hand afterwards.
 *
 * Round 1 of the S227 calibration was diagnosed by piping the artifact through an
 * ad-hoc Python one-liner: 11 of 14 decisions went to whichever answer was shown
 * first, and TIE was never returned. A yardstick that needs a separate manual step to
 * reveal it is broken will eventually be trusted on a day nobody runs that step, so
 * these counters now ride in the artifact's own summary.
 *
 * `always_first` is the damning one: an item where BOTH orderings picked the answer in
 * position 1 is an item the judge did not read.
 */
export function positionBiasTally(
  items: Array<{ order1?: { verdict: RawVerdict }; order2?: { verdict: RawVerdict } }>,
): { judged: number; always_first: number; always_second: number; raw_calls: number; raw_tie_calls: number } {
  const judged = items.filter((i) => i.order1 && i.order2);
  const verdicts = judged.flatMap((i) => [i.order1!.verdict, i.order2!.verdict]);
  return {
    judged: judged.length,
    always_first: judged.filter((i) => i.order1!.verdict === 'ANSWER_1' && i.order2!.verdict === 'ANSWER_1').length,
    always_second: judged.filter((i) => i.order1!.verdict === 'ANSWER_2' && i.order2!.verdict === 'ANSWER_2').length,
    raw_calls: verdicts.length,
    raw_tie_calls: verdicts.filter((v) => v === 'TIE').length,
  };
}

/**
 * Criterion 3 is "the answer conflicts with the registered gold passage on a number".
 * The S227 calibration caught this judge failing it in BOTH directions: it correctly
 * flagged `dig_teacher_digital_cpd_hours` (30 hours muddled into "30 至 150"), and it
 * invented a contradiction in `fin_ac_grant` — it read "無禮堂有蓋操場＝2 個特別室＝
 * $42,526" as inconsistent with "標準禮堂＝2.5 個特別室＝$53,158", when $53,158 / 2.5 × 2
 * is exactly $42,526. The judge does arithmetic between figures and gets it wrong.
 *
 * Money, ratios and hours are the most consequential class of fact in this knowledge
 * base, so a criterion-3 verdict is marked for human review rather than trusted or
 * silently dropped. Marked BEFORE anyone looks at the totals, so the mark cannot be
 * applied selectively to items whose verdict is inconvenient.
 */
export const REVIEW_CRITERION = 3;

export function needsHumanReview(item: {
  order1?: { deciding_criterion: number };
  order2?: { deciding_criterion: number };
}): boolean {
  return [item.order1, item.order2].some((o) => o?.deciding_criterion === REVIEW_CRITERION);
}

/**
 * The ship rule, fixed before the full run so the numbers cannot be interpreted after
 * the fact — S226's lesson was a broken ruler that produced the convenient conclusion.
 *
 * A WEAK_* verdict counts half: one ordering had a direction and the other called it a
 * tie, which is not a whole opinion. Items marked for human review are excluded from
 * the tally entirely rather than counted and caveated.
 *
 * `net_after` at or above `SHIP_THRESHOLD` is a ship case; below it the honest reading
 * is "no measurable answer-layer improvement", and the knob's only argument was a
 * retrieval-metric gain, so that reading means do not ship.
 */
export const SHIP_THRESHOLD = 8;

export function decisionTally(items: Array<{ combined: Combined; needs_human_review?: boolean }>): {
  counted: number; excluded_for_review: number; after_points: number; before_points: number;
  net_after: number; ship_threshold: number; verdict: 'SHIP_CASE' | 'NO_MEASURABLE_GAIN';
} {
  const counted = items.filter((i) => !i.needs_human_review);
  const points = (side: Side) =>
    counted.filter((i) => i.combined === side).length
    + 0.5 * counted.filter((i) => i.combined === `WEAK_${side}`).length;
  const after = points('AFTER');
  const before = points('BEFORE');
  const net = after - before;
  return {
    counted: counted.length,
    excluded_for_review: items.length - counted.length,
    after_points: after, before_points: before, net_after: net,
    ship_threshold: SHIP_THRESHOLD,
    verdict: net >= SHIP_THRESHOLD ? 'SHIP_CASE' : 'NO_MEASURABLE_GAIN',
  };
}

/** NFKC, because the rest of this project compares Chinese text after NFKC. */
export function norm(text: string | null | undefined): string {
  return (text ?? '').normalize('NFKC').trim();
}

export function isDecline(text: string | null | undefined): boolean {
  return norm(text) === norm(DECLINE);
}

/**
 * Decide whether an item needs the model at all. Identical text and mutual abstention
 * are ties by construction; spending two judge calls on them buys noise.
 */
export function shortcut(before: string | null, after: string | null): Combined | null {
  // Mutual abstention is checked FIRST: two declines are also byte-identical, and
  // "both sides abstained" is the fact S226 reported (8 of 38), so the more specific
  // label has to win or that count disappears into TIE_IDENTICAL.
  if (isDecline(before) && isDecline(after)) return 'TIE_BOTH_DECLINED';
  if (norm(before) === norm(after)) return 'TIE_IDENTICAL';
  return null;
}

/**
 * The rubric. Ordered by what actually went wrong in S226's hand read, hardest failure
 * first: wrong audience and self-contradiction outrank extra detail.
 */
export function buildPrompt(gold: GoldItem, first: string, second: string): string {
  const signatures = (gold.expected_passage_signature ?? []).filter(Boolean);
  const goldBlock = signatures.length
    ? signatures.map((s, i) => `（${i + 1}）${s}`).join('\n')
    : '（此題沒有登記答案段落簽名。）';
  const answerable = gold.answerable === false
    ? '此題在答案鑰匙中標示為【資料庫沒有答案】。恰當的回應是坦白表示找不到；作答並提供內容者較差。'
    : '此題在答案鑰匙中標示為【資料庫有答案】。坦白表示找不到者，較能正確作答者為差。';

  return [
    '你是香港教育政策問答系統的評分員。以下是同一條查詢的兩個候選答案，請判斷哪一個較佳。',
    '',
    `【查詢】${gold.query}`,
    gold.intent ? `【提問意圖】${gold.intent}` : '',
    `【答案鑰匙登記的原文段落】\n${goldBlock}`,
    `【可答性】${answerable}`,
    '',
    '【評分準則，由重到輕】',
    '1. 適用對象是否正確：把中小學或特殊學校的規定當成幼稚園的規定（或反之）屬嚴重錯誤，即使其餘內容豐富。',
    '2. 是否真的回答提問意圖：離題但內容充實者，差於簡短而切題者。',
    '3. 與登記段落是否一致：數字、期限、比例、條件如與登記段落衝突，屬嚴重錯誤。',
    '4. 內部是否自相矛盾：同一段先說「資料沒有載明」再給出具體數字，屬嚴重缺陷。',
    '5. 文句是否完整可發布：截斷句、重複詞污染、口語或提問句直接複製，屬缺陷。',
    '6. 在以上條件相同時，資料較齊備、較具體者為佳。',
    '',
    '【答案 1】',
    first,
    '',
    '【答案 2】',
    second,
    '',
    // S227 calibration round 1 found the judge picking whichever answer it saw first in
    // 11 of 14 decisions and never once returning TIE. Two mechanism fixes, not rubric
    // rewording: make it score each answer on its own before comparing (the same move
    // S214 used when it split the relevance judge into independent booleans), and
    // authorise TIE explicitly instead of demanding it name a deciding criterion.
    '請先分別檢視兩個答案各自違反了上述哪幾條準則（沒有違反則留空），然後才比較。',
    '兩者缺陷同級、且沒有一方在較高順位的準則上勝出時，必須回 TIE。TIE 是正常且常見的結論，'
    + '不要為了分出高下而放大細微差異；先後次序與答案長短都不是判斷理由。',
    '只依據上述準則判斷，不要猜測兩個答案的來歷。',
    '理由請用繁體中文書面語，一句起兩句止；若非 TIE，指出是哪一條準則造成差異，'
    + '並把 deciding_criterion 填該條編號；判 TIE 則填 0。',
  ].filter(Boolean).join('\n');
}

const VERDICT_SCHEMA = {
  name: 'pairwise_verdict',
  schema: {
    type: 'object',
    additionalProperties: false,
    required: ['answer_1_flaws', 'answer_2_flaws', 'verdict', 'deciding_criterion', 'reason'],
    properties: {
      // Scored per answer BEFORE the comparison, and listed first so the model fills
      // them first: an independent read of each answer is what a first-position
      // preference cannot survive.
      answer_1_flaws: { type: 'array', items: { type: 'integer', enum: [1, 2, 3, 4, 5, 6] } },
      answer_2_flaws: { type: 'array', items: { type: 'integer', enum: [1, 2, 3, 4, 5, 6] } },
      verdict: { type: 'string', enum: ['ANSWER_1', 'ANSWER_2', 'TIE'] },
      // Which numbered rubric line decided it (0 for TIE). Recorded so a run can be
      // audited for "the judge said audience but its reason talks about length".
      deciding_criterion: { type: 'integer', enum: [0, 1, 2, 3, 4, 5, 6] },
      reason: { type: 'string' },
    },
  },
} as const;

// --- self-test: pure functions only, zero network, zero spend -----------------
function selfTest(): number {
  const checks: Array<[string, boolean]> = [];
  const ok = (name: string, cond: boolean) => checks.push([name, cond]);

  // resolveSide: the whole point is that ANSWER_1 means a different side depending on
  // which side was shown first. Getting this backwards would silently invert every run.
  ok('resolveSide: ANSWER_1 with BEFORE first is BEFORE', resolveSide('ANSWER_1', 'BEFORE') === 'BEFORE');
  ok('resolveSide: ANSWER_1 with AFTER first is AFTER', resolveSide('ANSWER_1', 'AFTER') === 'AFTER');
  ok('resolveSide: ANSWER_2 with BEFORE first is AFTER', resolveSide('ANSWER_2', 'BEFORE') === 'AFTER');
  ok('resolveSide: ANSWER_2 with AFTER first is BEFORE', resolveSide('ANSWER_2', 'AFTER') === 'BEFORE');
  ok('resolveSide: TIE stays TIE', resolveSide('TIE', 'BEFORE') === 'TIE');

  // combine: the full truth table, because a winner recorded from one ordering alone is
  // exactly the position-bias artefact this tool exists to avoid.
  ok('combine: agreeing BEFORE', combine('BEFORE', 'BEFORE') === 'BEFORE');
  ok('combine: agreeing AFTER', combine('AFTER', 'AFTER') === 'AFTER');
  ok('combine: agreeing TIE', combine('TIE', 'TIE') === 'TIE');
  ok('combine: BEFORE then TIE is weak', combine('BEFORE', 'TIE') === 'WEAK_BEFORE');
  ok('combine: TIE then BEFORE is weak', combine('TIE', 'BEFORE') === 'WEAK_BEFORE');
  ok('combine: AFTER then TIE is weak', combine('AFTER', 'TIE') === 'WEAK_AFTER');
  ok('combine: TIE then AFTER is weak', combine('TIE', 'AFTER') === 'WEAK_AFTER');
  ok('combine: opposite winners are INCONSISTENT', combine('BEFORE', 'AFTER') === 'INCONSISTENT');
  ok('combine: opposite winners the other way', combine('AFTER', 'BEFORE') === 'INCONSISTENT');

  // shortcut: identical / mutually-declined pairs must cost zero calls.
  ok('shortcut: identical text', shortcut('甲乙丙', '甲乙丙') === 'TIE_IDENTICAL');
  ok('shortcut: identical after NFKC', shortcut('３０小時', '30小時') === 'TIE_IDENTICAL');
  ok('shortcut: both declined', shortcut(DECLINE, DECLINE) === 'TIE_BOTH_DECLINED');
  ok('shortcut: one declined is judged', shortcut(DECLINE, '有答案') === null);
  ok('shortcut: different text is judged', shortcut('甲', '乙') === null);
  ok('shortcut: null and empty count as identical', shortcut(null, '') === 'TIE_IDENTICAL');

  // The prompt must not leak which side is which, or the judge is scoring the label.
  const gold: GoldItem = {
    id: 't', query: '產假幾多星期', intent: '查產假時長',
    answerable: true, expected_passage_signature: ['14 星期有薪產假'],
  };
  const prompt = buildPrompt(gold, '答案甲', '答案乙');
  for (const leak of ['before', 'after', 'BEFORE', 'AFTER', 'rerank', 'RERANK', 'FEATURE_', 'knob', 'baseline']) {
    ok(`prompt does not leak "${leak}"`, !prompt.includes(leak));
  }
  ok('prompt carries the query', prompt.includes('產假幾多星期'));
  ok('prompt carries the intent', prompt.includes('查產假時長'));
  ok('prompt carries the gold signature', prompt.includes('14 星期有薪產假'));
  ok('prompt carries both answers', prompt.includes('答案甲') && prompt.includes('答案乙'));
  ok('answerable=true says abstention is worse',
    prompt.includes('【資料庫有答案】'));
  const noAnswer = buildPrompt({ ...gold, answerable: false }, 'a', 'b');
  ok('answerable=false says abstention is right',
    noAnswer.includes('【資料庫沒有答案】'));
  const noSig = buildPrompt({ ...gold, expected_passage_signature: [] }, 'a', 'b');
  ok('missing signature is stated, not silently dropped',
    noSig.includes('沒有登記答案段落簽名'));

  // The two mechanism fixes from calibration round 1. Both are load-bearing: without
  // the per-answer pass the judge compares positions, and without an explicit TIE
  // licence it never returns one (0 of 14 in round 1).
  ok('prompt asks for a per-answer pass before comparing', prompt.includes('請先分別檢視兩個答案各自違反'));
  ok('prompt authorises TIE explicitly', prompt.includes('必須回 TIE'));
  ok('prompt says order is not a reason', prompt.includes('先後次序'));
  const schemaProps = VERDICT_SCHEMA.schema.properties as Record<string, unknown>;
  ok('schema scores each answer separately',
    'answer_1_flaws' in schemaProps && 'answer_2_flaws' in schemaProps);
  ok('schema requires the per-answer fields',
    (VERDICT_SCHEMA.schema.required as readonly string[]).includes('answer_1_flaws'));
  ok('schema allows criterion 0 for TIE',
    ((schemaProps.deciding_criterion as any).enum as number[]).includes(0));

  // positionBiasTally: the counter that would have shown round 1 was broken without a
  // manual pass over the artifact.
  const bias = positionBiasTally([
    { order1: { verdict: 'ANSWER_1' }, order2: { verdict: 'ANSWER_1' } }, // never read it
    { order1: { verdict: 'ANSWER_2' }, order2: { verdict: 'ANSWER_2' } }, // second-position bias
    { order1: { verdict: 'ANSWER_1' }, order2: { verdict: 'ANSWER_2' } }, // consistent on content
    { order1: { verdict: 'TIE' }, order2: { verdict: 'TIE' } },
    {}, // shortcut item, never judged
  ]);
  ok('bias: counts only judged items', bias.judged === 4);
  ok('bias: catches always-first', bias.always_first === 1);
  ok('bias: catches always-second', bias.always_second === 1);
  ok('bias: counts raw calls', bias.raw_calls === 8);
  ok('bias: counts ties', bias.raw_tie_calls === 2);
  ok('bias: a content-consistent pair is not bias',
    positionBiasTally([{ order1: { verdict: 'ANSWER_1' }, order2: { verdict: 'ANSWER_2' } }]).always_first === 0);

  // Criterion-3 marking: the judge got this criterion wrong in both directions during
  // calibration, so a verdict resting on it is marked, and marking happens per item
  // rather than after the totals are visible.
  ok('review: marked when order1 decided on criterion 3',
    needsHumanReview({ order1: { deciding_criterion: 3 }, order2: { deciding_criterion: 2 } }));
  ok('review: marked when order2 decided on criterion 3',
    needsHumanReview({ order1: { deciding_criterion: 6 }, order2: { deciding_criterion: 3 } }));
  ok('review: not marked otherwise',
    !needsHumanReview({ order1: { deciding_criterion: 1 }, order2: { deciding_criterion: 0 } }));
  ok('review: a shortcut item with no orderings is not marked', !needsHumanReview({}));

  // The ship rule, asserted so it cannot drift after the numbers are in.
  const tally = decisionTally([
    { combined: 'AFTER' }, { combined: 'AFTER' },
    { combined: 'WEAK_AFTER' }, { combined: 'WEAK_AFTER' },
    { combined: 'BEFORE' },
    { combined: 'TIE' }, { combined: 'TIE_BOTH_DECLINED' },
    { combined: 'AFTER', needs_human_review: true },
  ]);
  ok('ship rule: review items are excluded', tally.counted === 7 && tally.excluded_for_review === 1);
  ok('ship rule: a weak verdict counts half', tally.after_points === 3);
  ok('ship rule: net is after minus before', tally.net_after === 2);
  ok('ship rule: below threshold is no measurable gain', tally.verdict === 'NO_MEASURABLE_GAIN');
  ok('ship rule: threshold is met at exactly 8',
    decisionTally(Array.from({ length: 8 }, () => ({ combined: 'AFTER' as Combined }))).verdict === 'SHIP_CASE');
  ok('ship rule: 7.5 net is not a ship case',
    decisionTally([
      ...Array.from({ length: 7 }, () => ({ combined: 'AFTER' as Combined })),
      { combined: 'WEAK_AFTER' as Combined },
    ]).verdict === 'NO_MEASURABLE_GAIN');
  ok('ship rule: ties do not move the needle',
    decisionTally([{ combined: 'TIE' }, { combined: 'TIE_IDENTICAL' }]).net_after === 0);

  // The calibration table is the answer key; assert its shape so a bad edit is loud.
  ok('calibration has the seven hand-read pairs', Object.keys(CALIBRATION).length === 7);
  ok('calibration covers both directions',
    Object.values(CALIBRATION).includes('BEFORE') && Object.values(CALIBRATION).includes('AFTER'));
  ok('calibration names hr_maternity as BEFORE', CALIBRATION.hr_maternity === 'BEFORE');

  // Agreement scoring: a weak win in the recorded direction still agrees; TIE and
  // INCONSISTENT do not, because the human read a direction.
  ok('agreement: exact match', agreesWith('BEFORE', 'BEFORE'));
  ok('agreement: weak match counts', agreesWith('WEAK_AFTER', 'AFTER'));
  ok('agreement: opposite does not', !agreesWith('BEFORE', 'AFTER'));
  ok('agreement: TIE does not', !agreesWith('TIE', 'AFTER'));
  ok('agreement: INCONSISTENT does not', !agreesWith('INCONSISTENT', 'AFTER'));

  const failed = checks.filter(([, pass]) => !pass);
  for (const [name, pass] of checks) {
    if (!pass) process.stdout.write(`FAIL  ${name}\n`);
  }
  process.stdout.write(
    failed.length === 0
      ? `ALL PASS (${checks.length} assertions)\n`
      : `${failed.length}/${checks.length} FAILED\n`,
  );
  return failed.length === 0 ? 0 : 1;
}

export function agreesWith(combined: Combined, human: Side): boolean {
  return combined === human || combined === `WEAK_${human}`;
}

// --- main ---------------------------------------------------------------------
async function main(): Promise<number> {
  if (process.argv.includes('--self-test')) return selfTest();

  const arg = (name: string): string | undefined => {
    const inline = process.argv.find((a) => a.startsWith(`--${name}=`));
    if (inline) return inline.slice(name.length + 3);
    const idx = process.argv.indexOf(`--${name}`);
    return idx > -1 ? process.argv[idx + 1] : undefined;
  };

  const runPath = arg('run');
  if (!runPath) throw new Error('--run <path to _s226_knobAB --synthesize .jsonl> is required');
  const calibration = process.argv.includes('--calibration');
  const label = arg('label') ?? 's227judge';
  if (!/^[a-z0-9_]+$/.test(label)) throw new Error('Invalid label');

  // Spend gate BEFORE any client exists (S214 convention).
  const approved = Number(arg('approved-max-calls'));
  if (!Number.isInteger(approved) || approved < 1) {
    throw new Error(
      'External API approval required: pass --approved-max-calls=N only after Leonard approves this exact batch.',
    );
  }

  const goldPath = arg('gold') ?? '../dev/_s213_gold_all.json';
  const gold = JSON.parse(fs.readFileSync(goldPath, 'utf8')) as GoldItem[];
  const goldById = new Map(gold.map((g) => [g.id, g]));

  const runRaw = fs.readFileSync(runPath, 'utf8');
  const rows = runRaw.split('\n').filter(Boolean).map((line) => JSON.parse(line) as any);
  const runSha = createHash('sha256').update(runRaw).digest('hex');

  const idsArg = arg('ids');
  const onlyIds = calibration
    ? new Set(Object.keys(CALIBRATION))
    : idsArg
      ? new Set(idsArg.split(',').map((s) => s.trim()).filter(Boolean))
      : undefined;
  let items = onlyIds ? rows.filter((r) => onlyIds.has(r.id)) : rows;
  const limit = Number(arg('limit'));
  if (Number.isInteger(limit) && limit > 0) items = items.slice(0, limit);
  if (calibration && items.length !== Object.keys(CALIBRATION).length) {
    throw new Error(
      `calibration needs all ${Object.keys(CALIBRATION).length} hand-read pairs; the run file has ${items.length}`,
    );
  }
  if (items.length === 0) throw new Error('nothing selected');

  // Worst case is two calls per non-shortcut item; refuse before spending anything if
  // the approval cannot cover the batch, rather than aborting half way through.
  const needsModel = items.filter(
    (r) => shortcut(r.before_synthesis ?? null, r.after_synthesis ?? null) === null,
  );
  if (needsModel.length * 2 > approved) {
    throw new Error(
      `batch needs up to ${needsModel.length * 2} calls (${needsModel.length} items x 2 orderings) `
      + `but only ${approved} approved`,
    );
  }

  const { createLlmClient } = await import('../src/lib/llmClient.js');
  const { getJudgeModel } = await import('../src/config/env.js');
  const judgeModel = getJudgeModel();
  const judge = createLlmClient({ model: judgeModel, maxRetries: 0 });

  const outDir = '../dev/source/eval_runs';
  const runDate = new Date().toISOString().slice(0, 10);
  const outPath = path.join(outDir, `${runDate}_${label}_rubric_judge.json`);
  if (fs.existsSync(outPath)) throw new Error(`${outPath} exists; preserve prior evidence`);

  const report: any = {
    label: `S227 pairwise rubric judge${calibration ? ' (calibration against the seven hand-read pairs)' : ''}`,
    generated_at: new Date().toISOString(),
    judge_model: judgeModel,
    source_run: runPath,
    source_run_sha256: runSha,
    gold_file: goldPath,
    mode: 'replay of saved answer texts; no retrieval, no Supabase, no embeddings',
    position_bias_control: 'each item judged twice with the sides swapped; agreement required for a winner',
    approved_max_calls: approved,
    attempted_api_calls: 0,
    items: [] as any[],
    summary: {},
  };
  const flush = () => fs.writeFileSync(outPath, JSON.stringify(report, null, 1) + '\n');

  const askJudge = async (prompt: string) => {
    if (report.attempted_api_calls >= approved) throw new Error('Approved API call cap reached');
    report.attempted_api_calls++;
    flush(); // written BEFORE the attempt, so an abort still shows what it spent
    const raw = await judge(prompt, VERDICT_SCHEMA as any);
    return JSON.parse(raw) as { verdict: RawVerdict; deciding_criterion: number; reason: string };
  };

  let done = 0;
  try {
    for (const row of items) {
      const g = goldById.get(row.id);
      if (!g) throw new Error(`${row.id} is not in the gold set`);
      const before = row.before_synthesis ?? null;
      const after = row.after_synthesis ?? null;
      const item: any = { id: row.id, query: g.query, domain: g.domain ?? null };

      const quick = shortcut(before, after);
      if (quick) {
        item.combined = quick;
        item.calls = 0;
      } else {
        // Order 1 shows the shipped side first; order 2 swaps them.
        const j1 = await askJudge(buildPrompt(g, before ?? '', after ?? ''));
        const j2 = await askJudge(buildPrompt(g, after ?? '', before ?? ''));
        const s1 = resolveSide(j1.verdict, 'BEFORE');
        const s2 = resolveSide(j2.verdict, 'AFTER');
        item.combined = combine(s1, s2);
        item.calls = 2;
        item.order1 = { shown_first: 'BEFORE', ...j1, resolved: s1 };
        item.order2 = { shown_first: 'AFTER', ...j2, resolved: s2 };
      }
      item.needs_human_review = needsHumanReview(item);
      if (CALIBRATION[row.id]) {
        item.human_verdict = CALIBRATION[row.id];
        item.agrees_with_human = agreesWith(item.combined, CALIBRATION[row.id]);
      }
      report.items.push(item);
      done++;
      process.stdout.write(
        `[${done}/${items.length}] ${row.id.padEnd(34)} ${String(item.combined).padEnd(18)}`
        + `${item.human_verdict ? ` human=${item.human_verdict} ${item.agrees_with_human ? 'AGREE' : 'DISAGREE'}` : ''}\n`,
      );
      flush();
    }
  } catch (e) {
    report.status = 'aborted';
    report.error = String(e);
    flush();
    process.stderr.write(`ABORTED after ${done}: ${String(e)}\n`);
    return 1;
  }

  const tally = (v: Combined) => report.items.filter((i: any) => i.combined === v).length;
  const judged = report.items.filter((i: any) => i.human_verdict);
  report.summary = {
    items: report.items.length,
    BEFORE: tally('BEFORE'), AFTER: tally('AFTER'), TIE: tally('TIE'),
    WEAK_BEFORE: tally('WEAK_BEFORE'), WEAK_AFTER: tally('WEAK_AFTER'),
    INCONSISTENT: tally('INCONSISTENT'),
    TIE_IDENTICAL: tally('TIE_IDENTICAL'), TIE_BOTH_DECLINED: tally('TIE_BOTH_DECLINED'),
    api_calls: report.attempted_api_calls,
    judge_health: positionBiasTally(report.items),
    needs_human_review: report.items.filter((i: any) => i.needs_human_review).map((i: any) => i.id),
    decision: decisionTally(report.items),
    ...(judged.length
      ? {
        calibration_items: judged.length,
        calibration_agree: judged.filter((i: any) => i.agrees_with_human).length,
        calibration_disagree: judged
          .filter((i: any) => !i.agrees_with_human)
          .map((i: any) => `${i.id}: judge=${i.combined} human=${i.human_verdict}`),
      }
      : {}),
  };
  report.status = 'complete';
  flush();
  process.stdout.write(`\n${JSON.stringify(report.summary, null, 1)}\nwrote ${outPath}\n`);
  return 0;
}

main().then((code) => process.exit(code)).catch((e) => {
  process.stderr.write(`${String(e)}\n`);
  process.exit(1);
});
