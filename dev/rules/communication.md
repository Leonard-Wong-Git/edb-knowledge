# Communication Pack

## Scope

Use for reply format, language behavior, output schema, user-facing explanation, and cross-agent handoff wording. Also governs **claim discipline**: what may be stated as established, and what must be marked unverified — including statements about the agent's own past actions.

## Load When

- User requests a specific response format, language, style, report, review, or schema.
- The task changes public-facing instructions or AI-facing reply discipline.
- **The reply will state a measurement, a count, a pass/fail rate, a root cause, or an account of what the agent did or did not do.** In practice this covers almost every substantive task, which is the intent: the claim rules below are worthless if they load only when someone is already thinking about wording.

## Rules

1. Match the user's language unless a project file requires another language.
2. Lead with decisions, findings, or results before background.
3. **A judgement requires a quotable source, or it is not stated.** Any written verdict — "this query is answerable", "this is the root cause", "this flag is benign", "this case is borderline" — must carry its evidence: the quoted text, file and line, or command output that supports it. If it cannot be quoted, write "未查" instead. Marking a claim unverified is not a fallback for laziness; it is the only honest option when the check has not been run.
4. Keep operational instructions copy-paste-ready when they are meant for future sessions.
5. Avoid exposing internal process unless it helps the user act.
6. **A search hit is not evidence; the opened passage is.** `grep` / `ilike` / a match count tells you where to look, never what is true. Any conclusion reached through a search must quote the matched context before it is stated.
7. **Before reusing a tool, test set, baseline or threshold, establish what it was built to measure.** Availability is not fitness. When the purpose changes, re-confirm each item under the new purpose and record that you did. An inherited instrument reports on its original question, not yours.
8. **After changing a set, reconcile the count. After changing text, read the diff.** A split, re-label or filter must leave the parts summing to the original, with every excluded item named and reasoned in the artifact itself. For file edits, `git diff` is the verification; "the old string is no longer found" is not, and cross-line regex on governance files is prohibited (playbook: `governance-file-edit-safety`).
9. **Statements about your own past actions must quote the record.** Cite the transcript, `git diff`, or file contents. If you cannot cite it, say "我核唔到" rather than describing from memory. Recollection of one's own behaviour is not a source.
10. **Direction of error is itself a trigger.** If a judgement, an omission, or a choice of words would make your own work look better, treat it as unverified and run rules 3, 6, 7, 8 and 9 before saying it. Do not rely on noticing that something feels wrong — a result that flatters you does not feel wrong. This clause exists because in S196 every error ran the same way: the residual defect was under-reported, three wrong calls were described as "no call was made", and off-topic material was accepted as benign.

## Checks

- Verify required headings, schema fields, or language split.
- Check public README or docs if user-facing behavior changed.
- Confirm handoff/opening messages are complete and root-specific when needed.
- Every number reported as a finding: name the instrument, confirm it was validated for this use, and show one inspected instance from behind the number.
- Every set that was re-partitioned: show the conservation check. Automate it as an assertion wherever the set lives in code, and prove the assertion fires by breaking it on purpose — a guard observed only in its passing state is untested.
- Every governance-file edit: report the `git diff` line delta and an inventory of the section anchors that must survive.

## Closeout

Record any durable response-format decisions and where they were persisted. If a claim made during the session was later corrected, record the correction next to the original in the log — a corrected number that only appears in the final message leaves the wrong figure standing in the persisted record.
