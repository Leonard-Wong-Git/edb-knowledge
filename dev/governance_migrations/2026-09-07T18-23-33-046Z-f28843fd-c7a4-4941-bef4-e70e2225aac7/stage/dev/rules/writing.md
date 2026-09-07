# Writing Pack

## Scope

Use for drafting, editing, style, structure, publication copy, documentation prose, and tone control.

## Load When

- User asks to write, rewrite, summarize, translate, or edit text.
- The task has a target audience, voice, format, or publication surface.

## Rules

1. Identify audience, purpose, and target surface before rewriting.
2. Preserve factual meaning unless the user asks for content changes.
3. Keep terminology consistent with project docs.
4. Mark uncertain claims instead of inventing support.
5. Do not bury durable requirements only in prose; use project index, spec, runbook, or handoff when needed.
6. For public Traditional Chinese docs or HTML aimed at non-technical readers, use steady written Chinese. Keep English only for commands, paths, URLs, file names, product names, and unavoidable tool names. Avoid mixed half-English fragments, internal governance codes, and developer-only wording in reader-facing prose.
7. For public README, onboarding, and other user-facing docs, use the product-journey rule: the user states the goal, the AI handles technical work. Keep one primary user path. Do not make users choose between install, upgrade, doctor, dry-run, or terminal commands when an AI-assisted path exists. Put technical commands in the dedicated AI install page, CLI help, or advanced examples instead of duplicating them in the main README flow.
8. When writing or revising Markdown files, decide whether the output is a durable source, a reference, a runbook, a public document, a reusable generated artifact, a draft, or one-time evidence. Durable outputs must be indexed or tied to a registered source/sync home before completion; drafts and one-time evidence must be labeled so they do not become hidden current state.
9. If a new document repeats requirements, instructions, acceptance rules, or process already owned by another file, consolidate into the existing source or make the new file explicitly subordinate. Do not let writing work create parallel truth.
10. For a translation or language counterpart of a user-facing document, the source-language document is the sole content authority unless the user explicitly changes the content. Read the whole source before drafting. Preserve its section order, cases, examples, figures, prompts, commands, confirmations, user-visible limits, navigation, and meaningful visual cues such as emoji; do not translate from an old counterpart, a summary, or remembered discussion.
11. Build a source-to-target section map before claiming completion. Do not compress several source steps into an overview, merge distinct user choices, reorder the journey, replace the source example with a different story, or add a new user rule, external action, format promise, or safety boundary that the source does not contain. If the source itself conflicts with the current product contract, flag that source drift and reconcile the source first; do not silently make the target language say something different.
12. A language counterpart needs semantic acceptance, not just mechanical checks. An independent reviewer who did not draft the target must read source and target section by section and decide: (a) what the source promises; (b) whether the target preserves the same action, limit, example, and consequence; (c) whether a reader can actually follow it; and (d) what user harm follows from a difference. Any mismatch is `FAIL`; correct the affected section and re-review it. File size, headings, keywords, emoji counts, links, HTML structure, or a similar overall gist are only mechanical floors and never a semantic pass.
13. For a release candidate or other durable public counterpart, record the semantic verdict and current source/target hashes in the existing candidate QA evidence **only when that language pair changed in the candidate**. Any source or target content change invalidates that pair's verdict and requires a new independent readback. Unchanged language pairs do not require a new review merely because another version is being released. A target may pass only when every mapped source section passes; do not claim a partial score as translation completion.

## Checks

- Verify requested format, language, and tone.
- Check links, commands, names, and version-sensitive claims when relevant.
- Check `dev/DOC_SYNC_REGISTRY.md` if public docs or user-facing instructions changed.
- For any Markdown file created or materially changed, check whether `dev/PROJECT_INDEX.md` needs a Directory Map, Fact Base, Entry Points, or read-condition update.
- Check duplicate-source risk before keeping a new requirement, checklist, process, or instruction document.
- For public Chinese docs, read the final text as a new user journey: the next action should be clear without technical background.
- For README-style docs, confirm the main path does not become parallel instructions: no repeated manual install section, no competing command table, and no requirement that the reader understand internal files before taking the first action.
- For a translation or language counterpart, complete the source-to-target semantic review above when the source or target changed. Record its verdict in the existing candidate QA owner when the document is public or release-bound; use hash, link, and format checks only to detect drift after the human review, not to replace it. Do not rerun an unchanged counterpart as a standing release ritual.

## Closeout

Record changed documents, unresolved content questions, and any sync or follow-up needed.
