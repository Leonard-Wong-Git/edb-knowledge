# Closeout Pack

## Scope

This pack is the single detailed contract for full Agent Handoff Kit closeout. Load it only for clear end-of-session or handoff intent. It does not authorize Git, release, publish, deployment, deletion, permission, or cleanup actions.

## Required Reads

Receive the current `dev/SESSION_HANDOFF.md` in full; in the same session, reuse only evidence already fully received from the unchanged file, and supplement every unread, truncated, or changed range. Read the current-session-relevant `dev/SESSION_LOG.md` entry, carry-forward risks, and any actual maintenance need. Read the affected complete command, route, rule, source, workspace mapping, and any required supplement in `dev/PROJECT_INDEX.md`; do not replace that reading with keyword hits. Classify every applicable `dev/DOC_SYNC_REGISTRY.md` obligation. Read `dev/PROJECT_DECISIONS.md`, integration rules, or another pack only when its closeout trigger or the session's actual work requires it.

## Write Contract

Use Kit markers as machine boundaries: `ack:section:*`, `ack:field:*`, `ack:log-entry:start/end`, and managed-core BEGIN/END. Human headings may be localized; markers may not be removed or translated.

- Current state, objective, recommended next action, active risk, blocker, required reading, workspace identity, and sync status belong in `dev/SESSION_HANDOFF.md`.
- When saving meaningful work changes, maintain the handoff's concise `Work Items` table using its declared fields, and keep project-wide name/goal in `PROJECT_INDEX` `Project`. Add the table/section to older projects only at an authorized state save when useful. Reconcile changed statuses against the evidence; do not duplicate full reports, rewrite old history, or create per-terminal-step records for the dashboard. Read-only dashboard viewing never triggers these writes.
- Chronological work and evidence disposition belong in `dev/SESSION_LOG.md`.
- File / command / source / capability maps belong in `dev/PROJECT_INDEX.md`.
- Recurring sync obligations belong in `dev/DOC_SYNC_REGISTRY.md`.
- Long-term evolution, architectural rationale, and accumulated learning belong in `dev/PROJECT_DECISIONS.md` when triggered.
- Reusable procedures belong in the relevant pack, registered reference, or QA check.
- `START_NEXT_SESSION_PROMPT.txt` is generated only from the handoff opening-message block.

Do not copy the full opening message into `dev/SESSION_LOG.md` or any third current governance file. The log records whether the mirror was verified no-op or regenerated and verified, plus an evidence reference when useful.

## Full Closeout

Full closeout is differential and write-minimal. Update only fields whose current truth changed. For unchanged state, preserve bytes where practical and record checked/no-op only when it helps the next agent. A same-session fully received unchanged source may be reused; incomplete, truncated, or changed sources require supplementary reading before relying on them. Reuse a completed task check only when its recorded root, task input, tool identity, commit / artifact identity, and required file hashes still match the current state. Do not rerun task QA that is already bound to unchanged identity. Do rerun checks affected by closeout writes, gates that are incomplete or indeterminate, closeout-specific checks, and the final `closeout-status` read-back. If a closeout attempt is interrupted, stopped, aborted, times out, or hits a spawn / transport error, resume at the first incomplete or indeterminate gate; do not restart from the beginning unless the root, input, tool identity, commit, artifact, or relevant hash changed.

Handoff cold zones are historical / evidence sections, old validation records, completed-work narratives, and unchanged durable anchors. Stable anchors and decision-changing current facts stay in the packet. Do not rewrite, reword, reorder, or refresh cold zones for ceremony or style. When older detailed narrative no longer changes the next action, preserve it byte-for-byte in existing trace/archive storage and verify that copy before removing it from the current packet. Do not rewrite or archive unchanged material at every closeout, impose an arbitrary size cap, or weaken the required full reception of the current packet.

1. Reconcile `dev/SESSION_HANDOFF.md`; never append a new current-state snapshot beneath an old one. Verify durable anchors, then update only changed closeout-reconciled fields or sections; leave already-current sections unchanged instead of rewriting them for ceremony.
2. Reconcile lifecycle state across `Completed This Session`, `Validation / QC`, `Next Priorities`, `Risks / Blockers`, and `Next Session Opening Message`. Completed or verified work cannot remain unresolved unless explicitly reclassified as monitor-only, follow-up scope, blocked, or reopened with its missing evidence or trigger.
   The bundled doctor is a mechanical floor for required lifecycle markers and readable sections only. `agent-handoff-kit closeout-status` checks explicit lifecycle declarations and same-scope textual contradictions; it does not prove natural-language semantic consistency. When it blocks, inspect its first `Resolved [...]` / `Carry-forward [...]` pair against the actual evidence: completion of one action does not complete another acceptance scope, and a preserved limitation is not a completion claim. Repair a real contradiction in its owning handoff section. If truthful, distinct scopes are misclassified, preserve the facts, report the checker defect and stop wording retries; do not add a reclassification prefix, invent a trigger, erase a limitation or broaden governance just to pass. A blocked result remains blocked until verified repair. Read all five sections as a whole before marking the lifecycle field resolved. For governance, release, or another project-defined high-risk completion, use the project's independent semantic review gate in addition to `closeout-status`.
3. Make `Next Priorities` name one recommended next action and a short reason unless blocked or a real user decision is required.
4. Complete the persistence-routing, handoff-sufficiency, `Closeout outcome`, and `Project-required persistence` fields. Apply the packet-only reconstruction check below before answering handoff sufficiency. The next agent must be able to continue from `AGENTS.md`, the handoff, the project index when needed, and routed packs without searching old log history. `complete` is allowed only when all required writes/read-backs and any project-required persistence succeeded; use `not_required` only when that persistence is genuinely not required. If a required commit, push, release record, or equivalent persistence is blocked or not authorized, set both fields to `blocked` with the exact boundary.
5. Add one concise log entry only for current work, risk, actual maintenance, or another durable fact that a later agent needs. Record evidence disposition and the prompt-mirror verification result when an entry is needed; omit the full opening message by design. A no-op closeout must not create a false work record.
6. Update the project index only when affected complete mappings, rules, or supplements changed. Classify every applicable sync-registry target as `confirmed`, `unverified`, `pending`, `blocked`, or `not_applicable`.
7. Run `agent-handoff-kit workspace-health --root <project root>` or equivalent read-only Git probes, then record only the last-verified root, Git root, branch, commit, worktrees / parallel workspaces, uncommitted changes, and unresolved drift. Do not clean or change them without separate authorization. Do not treat `dev/PROJECT_INDEX.md` or old handoff prose as the live worktree truth.
8. If the session used external tools or helper processes, apply the integrations and safety ownership rules. Close only task-owned resources. Retain shared, user-owned, other-agent-owned, system, or ambiguous resources unless separately authorized; state visibility limits.
9. Run the short maintenance assessment below. Record only actual maintenance work or a current risk; do not create a log entry solely to report a size advisory.
10. Mark first-use guidance `consumed` after the first successfully completed task or first full closeout. Upgrade must never reset `consumed` or `not_applicable` to `eligible`.
11. Verify `START_NEXT_SESSION_PROMPT.txt` against the sole fenced handoff opening-message block first. Regenerate it only when normalized content differs, then run the project's fixed prompt-mirror checker or perform an equivalent anchored read-back that verifies marker, heading, fence, full-copy uniqueness, and normalized content equality.
12. Run available project-specific closeout checks. Do not run a separate bundled `doctor`: the `closeout-status` command below performs the one required fresh doctor read-back. Do not treat an external update-check failure as local closeout failure. Fix state or mirror failures before claiming handoff ready.
13. Run `agent-handoff-kit closeout-status --root <project root>` after the handoff and prompt read-back. It performs the one required fresh doctor read-back plus a read-only workspace-health comparison against the handoff snapshot, and its output is the only final card source. A nonzero result means the closeout is blocked; do not replace it with a success summary.

## Packet-Only Reconstruction Check

Before closing out, reconstruct the next task using only the handoff, without chat memory, old logs or opening linked sources. Identify the parent outcome and consumer, the current step's relation to it, the exact resume point, remaining step/parent acceptance, and required sources with revision/freshness, reading scope/depth and unread gaps. Also recover decision-changing user corrections, reasons for accepted/rejected approaches, reusable artifacts with their evidence limits, every remaining consequential obligation and its downstream use, and permission/stop boundaries. Cite the owning handoff sections in `Reconstruction evidence`; do not create a second task summary. Then compare that reconstruction against the user's actual request and the relevant sources read this session. Missing, contradictory or assumed critical facts must be repaired in their existing handoff sections or explicitly recorded as blockers with the next clarification/read needed. Do not answer yes on labels or a successful CLI card alone: the CLI checks the recorded answer and evidence presence, not the truth of this reconstruction.

Check whether a reader could repeat a rejected attempt, redo accepted work, omit an obligation, act on obsolete instructions, or choose a plausible but wrong next action while still agreeing with the packet's headline. If so, preserve the missing decision-changing fact in its existing owning section, not merely in a linked historical log. Keep the packet sufficient and proportionate; do not paste the whole chat or silently discard important facts to fit an output limit. Transport truncation is handled by the core reception checkpoint, not by weakening the task.

Closeout verifies this session's saved packet. It cannot certify that a future reader received or understood it. Do not describe `closeout-status: complete` as successful future-session reception; the next agent must pass the core Handoff reception and recovery checkpoint independently.

Keep one `Answer:` line (`yes`, `no` or `unknown`, with optional explanation) and one `Reconstruction evidence:` line inside the marked sufficiency section. An affirmative answer requires concrete section references; keep `next-ai-can-continue` consistent. For an older handoff, add missing facts to its existing sections at this authorized closeout; upgrade must preserve user state and must not invent reconstruction evidence. Missing or negative answers, placeholder evidence and duplicate fields block `closeout-status` without changing project files.

Use only the depth needed to resume safely. A standalone task needs no invented parent tree; state that it is the whole task. Finishing a child does not complete its parent or authorize another step. Keep the next consequential action bounded by its input, output and acceptance; do not enumerate every future microstep. Keep decision-relevant terms and identifiers faithful; when a translation could change their meaning, retain the original term alongside it. Reading coverage is previous-session evidence, never permission for the next agent to skip required fresh source reads. Honest blocked-work handoff can be sufficient when the missing fact, impact and safe next action are explicit.

## Maintenance Trigger Check

Every full closeout runs this short assessment. It reports potential maintenance, but a pure `SESSION_LOG` size advisory is not a `closeout-status` blocker.

- SESSION_LOG: at 11 or more entries, more than 1500 lines, or a due 10-closeout backstop, report the shared maintenance advisory. Do full maintenance only when the current work establishes an actual preservation or continuation need, or a project-specific contract requires it. Keep recent safety-buffer entries; collapse only content already absorbed by an authoritative home. Before shortening an active source, verify the preserved copy. Archive older raw entries to `dev/SESSION_LOG_archive/archive_<batch>_<low_date>_to_<high_date>.md` and maintain `INDEX.md` only when archive work is actually performed. Unknown count alone does not force a historical sweep.
- PROJECT_DECISIONS: at 30 or more decisions-like handoff entries, assess whether actual long-term maintenance is needed; retain the newest 8–22 in the hot tier and move older decisions into the decisions archive only when that work is required. Write substantive task evolution, a multi-option architectural choice with rationale, or a cross-session learning when observed.
- Backstop: a known due 10-closeout count is an advisory to assess long-term maintenance. Do not infer a historical sweep from an unknown count; project-specific stricter requirements still apply.

If no actual maintenance applies, leave historical trace content unchanged. Handoff carries continuity; log and project decisions carry trace and long-term narrative.

## Opening Message And Card

The handoff opening-message block is authoritative. It must name the absolute root, route the agent through `AGENTS.md` and the handoff, state the current objective and boundary, and avoid instructing the next agent to redo completed work. It must not require SESSION_LOG as an ordinary startup read.

Use `agent-handoff-kit closeout-status --root <project root>` after the required read-backs. When it returns a card, copy the full card verbatim in a fenced `text` block before any explanation for both `status: complete` and `status: blocked`; never reduce it to selected status or blocker lines, print the literal placeholder `v<version>`, hand-compose a substitute success/blocked card, or use `handoff saved` unless the command reports `status: complete`. Only when no CLI card exists because the CLI could not be launched or returned no card may the final response show a fenced `closeout unavailable` card with no version and no `saved`/`complete` claim, followed by the actual missing condition. That presentation does not complete closeout and never replaces a returned complete or blocked CLI card.

```text
   /\_/\   Agent Handoff Kit v<version>
  ( -.- )  handoff saved
   > ^ <

status: complete
✅ Done: <completed summary>
🔎 QC: <validation summary>
📌 Handoff: opening message ready
⚠️ Boundary: <important boundary or none>
```

For `status: blocked`, the command instead says `handoff blocked`; retain that status, blocker reason, and human explanation: `這不是失敗；只是還有事未保存、未提交、未驗證或需要處理。先照 Blocker 行處理，不要把本輪當作已完成交接。` Then give the short local-root entry `Start Agent Handoff` / `開工` and the path-bearing fallback for an agent not yet pointed at the root. The narrow `closeout unavailable` presentation above is allowed only when there is no CLI card; do not use it to replace a returned blocked card or hand-compose a third stateful prompt.

## Stop Conditions

Do not claim closeout complete when any required write or read-back failed, lifecycle state conflicts remain, the mirror is stale or duplicated, the root is uncertain, mandatory sync is unclassified, `closeout-status` is nonzero, or required Git persistence was explicitly part of the project's closeout contract but did not succeed. State the exact blocker and leave the project in an honest resumable state.
