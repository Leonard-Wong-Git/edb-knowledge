# Closeout Pack

## Scope

This pack is the single detailed contract for full Agent Handoff Kit closeout. Load it only for clear end-of-session or handoff intent. It does not authorize Git, release, publish, deployment, deletion, permission, or cleanup actions.

## Required Reads

Read the current `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`, `dev/PROJECT_INDEX.md`, and `dev/DOC_SYNC_REGISTRY.md`. Read `dev/PROJECT_DECISIONS.md`, integration rules, or another pack only when its closeout trigger or the session's actual work requires it.

## Write Contract

Use Kit markers as machine boundaries: `ack:section:*`, `ack:field:*`, `ack:log-entry:start/end`, and managed-core BEGIN/END. Human headings may be localized; markers may not be removed or translated.

- Current state, objective, recommended next action, active risk, blocker, required reading, workspace identity, and sync status belong in `dev/SESSION_HANDOFF.md`.
- Chronological work and evidence disposition belong in `dev/SESSION_LOG.md`.
- File / command / source / capability maps belong in `dev/PROJECT_INDEX.md`.
- Recurring sync obligations belong in `dev/DOC_SYNC_REGISTRY.md`.
- Long-term evolution, architectural rationale, and accumulated learning belong in `dev/PROJECT_DECISIONS.md` when triggered.
- Reusable procedures belong in the relevant pack, registered reference, or QA check.
- `START_NEXT_SESSION_PROMPT.txt` is generated only from the handoff opening-message block.

Do not copy the full opening message into `dev/SESSION_LOG.md` or any third current governance file. The log records whether the mirror was verified no-op or regenerated and verified, plus an evidence reference when useful.

## Full Closeout

Full closeout is differential and write-minimal. Update only fields whose current truth changed. For unchanged state, preserve bytes where practical and record checked/no-op only when it helps the next agent. Reuse a completed task check only when its recorded root, task input, tool identity, commit / artifact identity, and required file hashes still match the current state. Do not rerun task QA that is already bound to unchanged identity. Do rerun checks affected by closeout writes, gates that are incomplete or indeterminate, closeout-specific checks, and the final `closeout-status` read-back. If a closeout attempt is interrupted, stopped, aborted, times out, or hits a spawn / transport error, resume at the first incomplete or indeterminate gate; do not restart from the beginning unless the root, input, tool identity, commit, artifact, or relevant hash changed.

Handoff cold zones are historical / evidence sections, old validation records, completed-work narratives, and unchanged durable anchors. Do not rewrite, reword, reorder, or refresh cold zones for ceremony or style. Change them only when the closeout directly proves their current meaning is false or the section itself is the named target of the reconciliation; otherwise preserve cold-zone bytes where practical and update only hot current-state fields.

1. Reconcile `dev/SESSION_HANDOFF.md`; never append a new current-state snapshot beneath an old one. Verify durable anchors, then update only changed closeout-reconciled fields or sections; leave already-current sections unchanged instead of rewriting them for ceremony.
2. Reconcile lifecycle state across `Completed This Session`, `Validation / QC`, `Next Priorities`, `Risks / Blockers`, and `Next Session Opening Message`. Completed or verified work cannot remain unresolved unless explicitly reclassified as monitor-only, follow-up scope, blocked, or reopened with its missing evidence or trigger.
   The bundled doctor is a mechanical floor for required lifecycle markers and readable sections only. The semantic lifecycle gate is `agent-handoff-kit closeout-status`; when it blocks, use its first `Resolved [...]` / `Carry-forward [...]` pair to repair the handoff, not a separate project workaround, repeated doctor runs, or a broader governance rewrite. Read all five sections as a whole before marking the lifecycle field resolved. For governance, release, or another project-defined high-risk completion, use the project's independent semantic review gate in addition to `closeout-status`.
3. Make `Next Priorities` name one recommended next action and a short reason unless blocked or a real user decision is required.
4. Complete the persistence-routing, handoff-sufficiency, `Closeout outcome`, and `Project-required persistence` fields. Apply the packet-only reconstruction check below before answering handoff sufficiency. The next agent must be able to continue from `AGENTS.md`, the handoff, the project index when needed, and routed packs without searching old log history. `complete` is allowed only when all required writes/read-backs and any project-required persistence succeeded; use `not_required` only when that persistence is genuinely not required. If a required commit, push, release record, or equivalent persistence is blocked or not authorized, set both fields to `blocked` with the exact boundary.
5. Add one concise log entry for work actually performed. Record evidence disposition and the prompt-mirror verification result; omit the full opening message by design.
6. Update the project index and sync registry only when their owned maps or obligations changed. Record each applicable sync target as `confirmed`, `unverified`, `pending`, `blocked`, or `not_applicable`.
7. Run `agent-handoff-kit workspace-health --root <project root>` or equivalent read-only Git probes, then record only the last-verified root, Git root, branch, commit, worktrees / parallel workspaces, uncommitted changes, and unresolved drift. Do not clean or change them without separate authorization. Do not treat `dev/PROJECT_INDEX.md` or old handoff prose as the live worktree truth.
8. If the session used external tools or helper processes, apply the integrations and safety ownership rules. Close only task-owned resources. Retain shared, user-owned, other-agent-owned, system, or ambiguous resources unless separately authorized; state visibility limits.
9. Run the short maintenance trigger check below and record its result in the log.
10. Mark first-use guidance `consumed` after the first successfully completed task or first full closeout. Upgrade must never reset `consumed` or `not_applicable` to `eligible`.
11. Verify `START_NEXT_SESSION_PROMPT.txt` against the sole fenced handoff opening-message block first. Regenerate it only when normalized content differs, then run the project's fixed prompt-mirror checker or perform an equivalent anchored read-back that verifies marker, heading, fence, full-copy uniqueness, and normalized content equality.
12. Run available project-specific closeout checks. Do not run a separate bundled `doctor`: the `closeout-status` command below performs the one required fresh doctor read-back. Do not treat an external update-check failure as local closeout failure. Fix state or mirror failures before claiming handoff ready.
13. Run `agent-handoff-kit closeout-status --root <project root>` after the handoff and prompt read-back. It performs the one required fresh doctor read-back plus a read-only workspace-health comparison against the handoff snapshot, and its output is the only final card source: copy its status faithfully. A nonzero result means the closeout is blocked; do not replace it with a success summary.

## Packet-Only Reconstruction Check

Before closing out, reconstruct the next task using only the handoff, without chat memory, old logs or opening linked sources. Identify the parent outcome and consumer, the current step's relation to it, the exact resume point, remaining step/parent acceptance, and required sources with revision/freshness, reading scope/depth and unread gaps. Cite the owning handoff sections in `Reconstruction evidence`; do not create a second task summary. Then compare that reconstruction against the user's actual request and the relevant sources read this session. Missing, contradictory or assumed critical facts must be repaired in their existing handoff sections or explicitly recorded as blockers with the next clarification/read needed. Do not answer yes on labels or a successful CLI card alone: the CLI checks the recorded answer and evidence presence, not the truth of this reconstruction.

Keep one `Answer:` line (`yes`, `no` or `unknown`, with optional explanation) and one `Reconstruction evidence:` line inside the marked sufficiency section. An affirmative answer requires concrete section references; keep `next-ai-can-continue` consistent. For an older handoff, add missing facts to its existing sections at this authorized closeout; upgrade must preserve user state and must not invent reconstruction evidence. Missing or negative answers, placeholder evidence and duplicate fields block `closeout-status` without changing project files.

Use only the depth needed to resume safely. A standalone task needs no invented parent tree; state that it is the whole task. Finishing a child does not complete its parent or authorize another step. Keep the next consequential action bounded by its input, output and acceptance; do not enumerate every future microstep. Keep decision-relevant terms and identifiers faithful; when a translation could change their meaning, retain the original term alongside it. Reading coverage is previous-session evidence, never permission for the next agent to skip required fresh source reads. Honest blocked-work handoff can be sufficient when the missing fact, impact and safe next action are explicit.

## Maintenance Trigger Check

Every full closeout runs this short check; full maintenance runs only when triggered.

- SESSION_LOG: trigger when the main log reaches at least 11 entries, exceeds 1500 lines, or the 10-closeout backstop is due. Keep recent safety-buffer entries; collapse only content already absorbed by an authoritative home. Archive older raw entries to `dev/SESSION_LOG_archive/archive_<batch>_<low_date>_to_<high_date>.md` and maintain `INDEX.md`. Port unique narrative before collapsing it.
- PROJECT_DECISIONS: trigger when a decisions-like handoff section has at least 30 entries; retain the newest 8–22 in the hot tier and move older decisions into the decisions archive. Also write substantive task evolution, a multi-option architectural choice with rationale, or a cross-session learning when observed.
- Backstop: every 10 closeouts, run the full long-term maintenance pass even when no semantic trigger is obvious. If the count cannot be determined confidently at the boundary, treat the backstop as due.

If no trigger applies, record one no-op reason. Handoff carries continuity; log and project decisions carry trace and long-term narrative.

## Opening Message And Card

The handoff opening-message block is authoritative. It must name the absolute root, route the agent through `AGENTS.md` and the handoff, state the current objective and boundary, and avoid instructing the next agent to redo completed work. It must not require SESSION_LOG as an ordinary startup read.

Use `agent-handoff-kit closeout-status --root <project root>` after the required read-backs. It renders the verified version when available and otherwise `version unverified`; never print the literal placeholder `v<version>`, hand-compose a substitute card, or use `handoff saved` unless the command reports `status: complete`.

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

For `status: blocked`, the command instead says `handoff blocked`; retain that status, blocker reason, and human explanation: `這不是失敗；只是還有事未保存、未提交、未驗證或需要處理。先照 Blocker 行處理，不要把本輪當作已完成交接。` Then give the short local-root entry `Start Agent Handoff` / `開工` and the path-bearing fallback for an agent not yet pointed at the root. Do not hand-compose a third stateful prompt in the final response.

## Stop Conditions

Do not claim closeout complete when any required write or read-back failed, lifecycle state conflicts remain, the mirror is stale or duplicated, the root is uncertain, mandatory sync is unclassified, `closeout-status` is nonzero, or required Git persistence was explicitly part of the project's closeout contract but did not succeed. State the exact blocker and leave the project in an honest resumable state.
