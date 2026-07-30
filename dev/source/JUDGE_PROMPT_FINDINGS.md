# Anti-confabulation judge — what was measured in S196, and what to do next

Status: **finding recorded, nothing shipped.** `RELEVANCE_JUDGE_PROMPT` in
`backend/src/api/searchChannelB.ts` is unchanged. Read this before touching it.

## ⚠️ S199 — READ THIS FIRST: the model below matters more than any prompt in this file

**Production does not run the model this file's earlier findings were measured on.**
`env.ts` falls back to `gpt-4.1-nano`, and `backend/README.md` and `DEPLOY_CHANNEL_B.md`
both show that value — but the Render service sets **`OPENAI_MODEL=gpt-4o-mini`**
(confirmed by Leonard in the dashboard Environment tab, 2026-07-30). Nothing outside
Render can read it: `/health` does not report the model and the OpenAI API will not say
which model a key is used with. It has to be re-confirmed in the dashboard before any
judge measurement is quoted as production behaviour.

S199 first measured on the code default and got a completely different judge. The two
runs are kept, relabelled `_nano_ARTIFACT`, because the contrast is itself the finding:

| prompt | model | primary | answer half | decline half | false answers |
|---|---|---|---|---|---|
| shipped | gpt-4.1-nano (**not production**) | 11/22 | 0/11 | 11/11 | 0 |
| shipped | **gpt-4o-mini (production)** | 18/22 | **8/11** | 10/11 | **1** |
| V3 | gpt-4.1-nano (**not production**) | 18/22 | 7/11 | 11/11 | 0 |
| V3 | **gpt-4o-mini (production)** | **21/22** | **11/11** | 10/11 | **1** |

On the code default the judge is close to a constant 否 — 0/11 on cases whose answer is
verbatim in the chunks. **On the model production actually runs, the same prompt answers
8 of 11.** The prompt was never the whole story; the model was carrying most of it.

### What this does to the rest of this document

The S196 finding below ("the shipped judge declines essentially everything", 8/16, all
eight answerable cases declined) is **unverified against production**. Its harness was
never committed, so which model it used cannot be recovered — but its result reproduces
the nano behaviour closely and does not resemble the production-model behaviour at all.
Treat 8/16, the 「寧緊莫鬆」 diagnosis and "V3 recovers 3" as measured against a model the
service does not run, until someone re-measures. **Do not delete them** — they are the
evidence trail for a real defect, just possibly not the defect that ships.

The consequence for planning is larger than the numbers. The recorded order of work —
「先修 judge，後收 bypass」 — rests on S196 having put two answerable controls to "the real
judge" and seeing both declined. If that was the code default, the premise no longer
holds, and narrowing the footnote bypass may now be affordable. That has to be
re-measured, not assumed in either direction.

### The measurement was controlled before it was believed

`--plumbing-check` runs two blunt S177-era scenarios through the same prompt, model and
call path, and both return 能 on either model. So the all-否 nano result was a genuine
verdict rather than broken wiring. The check caught nothing — and it still earned its
place, because the wiring fault it rules out would have produced exactly the output S199
was expecting to see (S198's silent-instrument trap). It did not, however, protect
against the failure that actually happened: **the harness was wired correctly to the
wrong model.** A control proves the instrument responds; it says nothing about whether
the instrument is pointed at the system under test. That question — "is this the thing
production runs?" — has to be asked separately, and for anything Render-side it can only
be answered in the dashboard.

### What the acceptance set is, and what it is not

- Answer half: every 16th question-led curated footnote (after dropping the four topics
  S196 tuned against), asked using **the footnote's own question** — authored by whoever
  curated the fact, not by whoever is tuning the prompt. In all 11 the origin footnote
  returns at rank 1, so the answer is verbatim in what the judge sees.
- Decline half: 10 fresh gap / neighbouring-question cases absent from `judge_probe.py`
  and `footnote_lead_probe.py`, plus `D00_s177_frozen_post`, which keeps the **original
  pre-fix chunks** of the S177 incident (live retrieval would now answer it legitimately,
  since the TRG 10% footnote was ingested as the fix). Three are composite traps —
  a student medical-certificate question whose chunks state the staff rule verbatim, a
  record-retention question carrying "3 years" for purchase records and "7 years" for KG
  accounts but no period for student records, and an air-conditioner replacement question
  carrying a 12-month interval that belongs to fire equipment.
- **Not** an unbiased sample of user traffic, and not externally sourced. Its honesty
  rests on being frozen before measurement and on every label being read off a passage.
- Two bare-noun cases are scored apart because calling them answerable is the project's
  S183/S195 position, not a passage reading.

### The bar for shipping a candidate

Unchanged in substance, now with a number attached: beat 0/11 on the answer half **while
keeping 11/11 on the decline half**. One false answer is a stop, and a false answer on
`D00_s177_frozen_post` is disqualifying regardless of the rest. Re-run
`footnote_lead_probe.py` after deploying.

## S199 — what the frozen set found on the production model

Runs: `2026-07-30_s199_shipped_4omini.json` / `2026-07-30_s199_v3_4omini.json`. Prompt
file `dev/source/judge_prompts/v3_s196.txt`, asserted verbatim against the V3 block below.

**V3 is better than shipped on the production model too**: 11/11 on the answer half
against shipped's 8/11, recovering `A02` (permit cancellation), `A05` (DSS fee-remission
criteria) and `A06` (three-tier mechanism), with no decline lost. V3 was never tuned
against this set — it came from S196's sixteen cases, which share no query with these
twenty-four — so that is a held-out result.

**But both prompts fail the same case, and that case is live.**

### The one thing this session found that is shipping wrong today

`D01_student_sickleave` — 「學生請病假要唔要交醫生紙」. The retrieved chunks state, verbatim,
the rule for **staff**: 資助學校教師同非教學人員…申請病假超逾兩天必須出示有效的醫生證明書.
Nothing in them is about students. Both the shipped prompt and V3 answer 能, and the live
endpoint returns a confident synthesis telling the user that a student needs a medical
certificate after two days, explicitly reasoning across from the staff rule.

Verified against the live endpoint on 2026-07-30, quoting the answer it returned:
「當學生請病假超過兩天時，必須出示有效的醫生證明書」, followed by
「月薪教職員在病假方面若申請超過兩天則必須提交醫生證明」. It transplants the staff rule onto
students and states it as policy. This is the S177 class — a rule that exists, applied to
a subject it does not cover — and it is what a user gets right now.

**Fixing the judge prompt does not fix it.** The lead on that query is a
`footnote_curated` chunk at 0.574, so the footnote bypass applies and the judge is never
called. The defect lives in the bypass path that S196 wanted to narrow and deferred.

That deferral was justified by measuring the two affected controls against "the real
judge" and seeing both declined — a measurement whose model cannot now be verified. On
`gpt-4o-mini` the judge answers 8/11 of the answerable half unaided, and 11/11 under V3.
**The stated reason for not narrowing the bypass may no longer hold.** Re-measure before
acting on it in either direction.

### Still open

- Bare-noun cases `S01`/`S02` (人工智能初探, ICT 課程指引) decline under both prompts on the
  production model. That is the S194/S195 complaint, still unresolved, and it is a
  separate axis from the confabulation one.
- The decline half is 11 cases and one of them is already a miss. One false answer out of
  eleven is not a safety estimate; it is a warning. The set needs widening before any
  prompt change is argued from it — 14 further gap candidates were retrieved in S199 and
  are awaiting per-passage labelling.
- Shipping V3 still needs a §3 PLAN, Leonard's decision on the risk, and a live re-run of
  `footnote_lead_probe.py` afterwards. Note that V3 changes nothing about `D01`.

## The finding

The shipped judge declines essentially everything.

Measured by calling the judge directly (same prompt, same model, real top-5 chunks pulled
from the live endpoint) over 16 cases — 8 that the corpus genuinely answers, 8 that it
genuinely does not:

| prompt | correct | false answers | notes |
|---|---|---|---|
| shipped | **8/16** | 0 | declined all 8 answerable cases, including four whose answer is verbatim in the retrieved chunk |
| shipped minus the 「寧緊莫鬆」 paragraph | 9/16 | 0 | that paragraph is doing most of the damage |
| V3 (below) | **11/16** | 0 | recovers 3, keeps every decline |
| V4 (longer, two query shapes) | 8/16 | 0 | more elaborate instructions made it worse |

Cases it declines although the answer is present word-for-word:

- 「老師病假連續請幾耐先要交醫生紙」 → chunk says 申請病假超逾兩天必須出示有效的醫生證明書
- 「體罰投訴要幾多日內處理完」 → chunk says 建議在接獲投訴起計兩個月內完成…十四天內提出上訴
- 「校服供應商招標要幾多間報價」 → chunk says 超過$200,000須公開招標、邀請最少5個供應商
- 「幼稚園每班最多可以收幾多個學生」 → chunk says 每班學生人數不應超過30人

This is why production looks fine: the judge is bypassed for a curated-footnote lead and
for a vault lead ≥ `VAULT_LEAD_SCORE`, so on the paths users hit most, it never runs. The
judge is not protecting those answers — the bypasses are carrying them. Where the judge
*does* run, it is close to a constant 否, which is the same behaviour S194 and S195B
recorded as "the judge over-declines" without identifying the cause.

## Why this blocks the other work

S196 wanted to narrow the footnote judge-bypass so that a footnote which merely grazes the
query has to face the judge. Five queries still take a lead they should not: two answer the
NEIGHBOURING question (「教師每年可以請幾多日大假」 → sick-leave footnote; 「學校每堂補習費
可以收幾多」 → other approved fees), and three have no basis in the corpus at all — of which
「學校可唔可以借錢俾教職員」 is the sharpest: nothing anywhere states a rule about a school
lending to staff, yet the system answers it with conviction. Measured
coverage-ratio separation is clean (negatives 0.40 / 0.62, positives p10 0.77), so the gate
itself is buildable at ratio ≥ 0.70 — it would cost the bypass on two answerable controls.

**Do not ship that gate while the judge is in this state.** Both controls were put to the
real judge and it declined both. Narrowing the bypass today converts two correct answers
into 「未能找到」 in exchange for suppressing two neighbouring-question answers, which is a
net loss. Order of work is therefore: fix the judge first, then narrow the bypass.

## The V3 candidate (not shipped)

The change that helped was structural, not tonal: state the decision as a test applied to
the text, instead of as a mood. 「有任何不確定，一律答否」 reads to the model as a global
confidence question, and it resolves it as 否 nearly every time.

```text
判斷下面「資料」有冇直接回答「問題」。

規則：
- 問題問緊一個具體事項（數字／期限／上限／比例／條件／責任／規則）。喺資料搵嗰個事項。
- 資料明文講到嗰個事項就答「能」，措辭唔同唔緊要。例如問「幾耐要交醫生紙」而資料寫「超逾兩天須出示醫生證明書」＝能；問「營辦商責任」而資料列出營辦商須做嘅事＝能。
- 問題問嘅事項喺資料搵唔到，只有同一大主題下嘅另一件事，就答「否」。例如問「大假幾多日」而資料只有「病假幾多日」＝否；問「補習費上限」而資料只有其他收費項目＝否。
- 唔好用相近但唔同嘅數字或概念頂替。頂替＝否。

只回答一個字：能 或 否。

問題：{QUERY}

資料：
{CHUNKS}
```

## What is needed before shipping it

The 16 cases above were assembled and then iterated against, so V3's 11/16 is a tuned
number and will not hold at that level on unseen queries. Before this or any successor
prompt goes to production:

1. **Build an untuned acceptance set.** The decline half matters most: it must include the
   S177 class (凍結教席 → IMC 60%), which V3 still declines correctly, plus fresh
   neighbouring-question cases nobody tuned against. Draw the answer half from curated
   footnotes' own facts, since those have a verifiable ground truth.
2. **Measure the shipped prompt on it first**, so the comparison is against reality rather
   than against the assumption that the judge currently works.
3. **Count false answers separately from accuracy.** A prompt that answers more is only an
   improvement if the decline set stays intact; one false answer on a number is worse than
   several declines (S177 is the precedent).
4. Re-run `footnote_lead_probe.py` after deploying, because a judge that answers more
   changes what the lead gate is protecting.

## Reproducing the measurement

Chunks are fetched once from the live endpoint and cached, then prompt variants are scored
offline — no deploy is needed to iterate, and that is the reason this could be measured at
all. Fetch top-5 per query via `POST /api/search/channel-b` with `synthesize:false`, store
`{query, want, chunks}`, then call `createLlmClient()` from `backend/src/lib/llmClient.ts`
with the candidate prompt and count verdicts starting with 能.
