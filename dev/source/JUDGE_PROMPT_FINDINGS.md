# Anti-confabulation judge — what was measured in S196, and what to do next

Status: **finding recorded, nothing shipped.** `RELEVANCE_JUDGE_PROMPT` in
`backend/src/api/searchChannelB.ts` is unchanged. Read this before touching it.

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
