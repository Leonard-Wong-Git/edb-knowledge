# Anti-confabulation judge — what was measured in S196, and what to do next

Status: **V3 SHIPPED (S200, 2026-07-30).** `RELEVANCE_JUDGE_PROMPT` in
`backend/src/api/searchChannelB.ts` now holds the V3 prompt (byte-identical to
`dev/source/judge_prompts/v3_s196.txt`; `judge_acceptance.py` `SHIPPED_PROMPT` updated in
lockstep, `--check-parity` green). Read the S200 ship record below before touching it again.

## S200 — SHIPPED with a documented gate override (Leonard, Option 2)

V3 replaced the shipped prompt. Acceptance evidence is `2026-07-30_s199_v3_4omini.json`
(prompt byte-identical to what now ships): primary **21/22**, answer-half **11/11** (recovers
`A02`/`A05`/`A06` over shipped's 8/11), decline-half **10/11**, `D00_s177_frozen_post` = 否
(correct), false answers = **[`D01_student_sickleave`]**.

**The gate says stop; it was overridden on purpose.** DOC_SYNC row 41 and the bar below read
"any false answer on the decline half = 唔准 ship". V3 has one — `D01`. It shipped anyway on
this reasoning, recorded per AGENTS §2 rule 6 (override logged in SESSION_LOG S200):

1. **Not a regression.** The currently-live prompt fails `D01` identically (能) — see
   `2026-07-30_s199_shipped_4omini.json`. V3 introduces **zero** new false answers and
   recovers three correct declines-to-answers. Every measured axis is ≥ the live baseline.
2. **The disqualifier does not fire.** `D00_s177_frozen_post` is correctly declined.
3. **`D01` is not judge-served in production.** Its lead is a `footnote_curated` chunk at
   0.574 > `FOOTNOTE_LEAD_SCORE` 0.45, so the footnote bypass fires and the judge is never
   called on it. The harness verdict is the judge's counterfactual, not live behaviour;
   shipping V3 changes nothing about `D01` live. `D01` belongs to NEXT ④ (narrow the bypass).

So the override trades a literal-gate pass for a change that is strictly better than the
status quo on everything the judge actually gates. What it does **not** do: fix `D01` live —
a user asking 「學生請病假要唔要交醫生紙」 still gets the staff rule transplanted onto students,
because that path skips the judge. That is unchanged by this ship and remains the top open
defect for the coupled bypass work.

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

### S199 — the footnote bypass, measured live, and why judge-first still holds

Run: `dev/source/judge_runs/2026-07-30_s199_footnote_bypass_live.json`.

`D01` is not one bad query; it is a class. Seven fresh queries whose top hit is a curated
footnote (so the footnote bypass may fire and the judge is skipped) were sent to the live
endpoint with `synthesize:true`. **All seven produced a confident answer. None declined.**

But "answered" is not "fabricated", and reading each answer against the corpus splits them:

- **`D17` 「學校要幾耐做一次消防演習」 — confirmed live fabrication.** 消防演習 / 消防演練 /
  逃生演習 appear **0 times** in the store. The answer states drills happen 每12個月, a
  figure transplanted from the 消防裝置 *inspection* interval. A user is told a made-up
  drill frequency, with conviction.
- **`D13` 「學校可以收幾多錢留位費」 — the answer was CORRECT.** The corpus states the K1
  註冊費／留位費 cap at 970 half-day / 1,570 full-day (`g26`, `k1_admission_2627`,
  `kg_admin_guide_2026`, all with a url). This query was mislabelled here as a gap; the
  footnote lead did exactly its job. (Recorded because the mistake ran toward the flattering
  direction — more fabrications makes this finding look bigger — and was caught only by
  opening the chunks, not by the label feeling wrong. Same shape as the S196/S197 lessons.)
- The other five range from a defensible unsourced negative (`D11`) to neighbouring-rule
  transplants (`D20`, `D23`) to one that could not be confirmed as a gap at all (`D15`).

So the honest headline is **not** "the bypass fabricates everything". It is: **the footnote
path answers gap queries instead of declining them, at least one of those answers is a
fabricated figure, and at least one is correct.**

That last clause is the important one. The bypass cannot simply be removed, because `D13`
shows it also carries right answers a judge would have to pass. The fix is therefore
coupled, not sequential-optional: these footnote-lead cases have to be routed through a
judge that both declines `D17` and passes `D13`. On the production model (`gpt-4o-mini`)
the shipped judge already answers 8/11 of the answerable half and V3 answers 11/11 while
declining every gap — so a judge that can do both is within reach, but it must be trusted
FIRST, then the bypass narrowed to send these cases to it. **The recorded order — fix the
judge, then narrow the footnote bypass — holds.** (An earlier S199 remark that "fixing the
judge does not fix D01" was half-right: the judge never runs on D01 today, but fixing it is
the precondition for making the bypass send D01 to it.)

### Still open

- Bare-noun cases `S01`/`S02` (人工智能初探, ICT 課程指引) decline under both prompts on the
  production model. That is the S194/S195 complaint, still unresolved, and it is a
  separate axis from the confabulation one.
- ~~The decline half is 11 cases and one of them is already a miss... 14 further gap
  candidates were retrieved in S199 and are awaiting per-passage labelling.~~ **DONE S201
  (2026-07-31, ②b).** The 14 S199 candidates were never persisted, so S201 authored 14
  fresh in-domain candidates and labelled each by reading all five fetched passages before
  any judge verdict. Result: 10 clean gaps added to the decline half (now **21**, so D01's
  known miss is 1/21 not 1/11) + 1 answerable control added to the answer half (GN11
  procurement >$200k, same D13 shape). 3 of 14 flipped against the pre-read hypothesis
  (GN06 gap→answerable, GN10 answerable→gap, GN12 gap→answerable) = passage-driven. Dropped:
  GN01 (borderline). Kept as findings not cases: GN06, GN12 (both read answerable). D01's
  decline label is now also confirmed by Leonard's domain note (student sick-leave doctor's
  note = school-based, no EDB source → decline is correct; the live 能 is the defect). The
  set is frozen at 12 answer / 21 decline / 2 secondary; **it has NOT yet been scored** —
  measuring the shipped/candidate prompt on the widened set is NEXT ②'s job (a §3 change
  that must reconfirm `OPENAI_MODEL` in the dashboard first).
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
