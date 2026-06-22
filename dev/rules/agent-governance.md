# Agent Governance Pack

## Scope

Use for governance rules, prompts, agent instructions, handoff systems, startup/closeout behavior, skills, and rule packs.

## Load When

- User asks to change AI behavior, project governance, prompts, handoff, startup, closeout, or tool-use rules.
- A change affects `AGENTS.md`, `dev/*`, rule packs, installer templates, or durable workflow docs.
- User asks to "治理打通", "把文件接入 Agent Handoff Kit", "接入 Agent Handoff Kit", "掃描未接入 Agent Handoff Kit 的重要文件", "bridge governance", "connect this document to governance", or scan for unbridged governance documents.
- User asks to make something long-term, cross-session, reusable, "寫入長期治理", "轉成長期機制", "之後都要遵守", or says future sessions should remember an API / MCP / tool-use pattern.

## Rules

1. Locate the existing source of truth before adding a rule.
2. Prefer merge, replace, or registry rows over append-only rule growth.
3. Keep public runtime rules generic; project-specific incidents belong in logs, runbooks, or project index.
4. Do not let development-only workspace rules enter public runtime.
5. Check complexity budget before adding default-core behavior.
6. Before creating durable workflow, runbook, or instruction files, first classify the knowledge type and verify whether an existing home can carry it without a new file: current state belongs in `dev/SESSION_HANDOFF.md`; trace evidence belongs in `dev/SESSION_LOG.md`; file / command / reference maps belong in `dev/PROJECT_INDEX.md`; sync obligations belong in `dev/DOC_SYNC_REGISTRY.md`; reusable operating procedures belong in the relevant rule pack or registered reference. New runbooks are last resort only.
7. When a task uses external skills, subagents, demo workspaces, or another tool's closeout, treat those flows as subordinate to the active root's Agent Handoff Kit governance. The active root still needs the `runtime-core/AGENTS.core.md` persistence gate decision; do not duplicate the gate thresholds in this pack.
8. For long-running projects, maintain `dev/PROJECT_DECISIONS.md` per R-028 closeout discipline (see `runtime-core/AGENTS.core.md` closeout maintenance trigger check): capture major decisions when they happen, run the short trigger check at every closeout, and do full long-term maintenance only when a hard trigger, semantic trigger, or 10-closeout backstop applies. Short single-task projects keep this as a no-op default; users are not expected to edit this file manually.
9. Governance bridge is a triggered review, not a default startup scan. Use it when an important file, source-of-truth document, runbook, production guide, workflow, checklist, stock list, or similar durable document may need to be connected to project governance.
10. Content-based trigger: long-term governance routing is content-based, not trigger-only. Even if the user does not say "轉成長期機制" or "寫入長期治理", treat a statement as durable governance when it says future sessions must follow it, when it corrects a recurring AI mistake, or when it defines a reusable API / MCP / tool-use pattern. Do not persist long-term governance knowledge only in `dev/SESSION_LOG.md`, `dev/SESSION_HANDOFF.md`, or `START_NEXT_SESSION_PROMPT.txt`; those surfaces may be compressed, archived, or regenerated.

## Governance Bridge Workflow

Use this workflow when the user asks for governance bridge / 治理打通 / 把文件接入 Agent Handoff Kit / 接入 Agent Handoff Kit / connect this document to governance, or asks to scan for unbridged governance documents / 掃描未接入 Agent Handoff Kit 的重要文件.

1. Identify the target. If the user named a file, inspect that file and its surrounding directory. If no file is named, run a bounded repo scan for likely durable documents such as source-of-truth files, runbooks, workflows, guides, checklists, stock lists, production guides, and rules.
2. Check the target file itself: it should state its role, scope, update trigger, owner or responsible workflow when known, and what must not be inferred from it.
3. Check `dev/PROJECT_INDEX.md`: the file should be discoverable with its role and "read when" condition. Source-of-truth or reference files should appear in Fact Base, External Sources, Directory Map, Entry Points, or another existing indexed home that fits the project.
4. Check `dev/DOC_SYNC_REGISTRY.md`: future same-type changes should have a matching change type or an explicit reason no durable sync rule is needed.
5. Check related workflows, guides, runbooks, or rule packs: if a process creates or updates the file, that process should say when to update the file or its index row.
6. Check `dev/SESSION_HANDOFF.md`: only current state, next action, unresolved risk, blocker, or a startup-needed fact should be in handoff. Do not copy whole documents or old evidence into handoff.
7. Check `dev/SESSION_LOG.md`: this session's bridge review, validation, and evidence can be logged when it affects future action, but log entries must not become current state.
8. Search for duplicate source-of-truth risk. If another file has the same durable role, recommend merge, reference, or retire options; do not delete, rename, or move files without explicit approval.

For repo-wide scans, report candidates as candidates. Do not fail ordinary docs merely because they are not indexed; only durable files that future agents need to discover, update, or distinguish from drafts should be bridged.

## Long-term Governance Routing

Use this workflow when the user asks to write something into long-term governance, turn an experience into a mechanism, make a rule apply across sessions, or when the content itself clearly has durable force.

1. Classify the knowledge before writing:
   - Current task state, next action, unresolved risk, or startup-needed fact -> `dev/SESSION_HANDOFF.md`.
   - Chronological evidence or validation trace -> `dev/SESSION_LOG.md`.
   - File maps, command maps, API reference locations, tool capability maps, and external source coordinates -> `dev/PROJECT_INDEX.md`.
   - Sync obligations or external mirror duties -> `dev/DOC_SYNC_REGISTRY.md`.
   - Durable decisions, architecture trade-offs, research-derived rationale, and long-term lessons -> `dev/PROJECT_DECISIONS.md`.
   - Reusable procedures, recurring mistake prevention, API / MCP / tool-use rules -> the relevant rule pack, registered reference, or QA check.
   - API / MCP / tool-use patterns -> project index / registered reference / integrations pack, depending on scope.
2. If the knowledge is reusable but no existing home fits, propose the smallest new registered reference or rule-pack patch. New runbooks remain last resort.
3. If the knowledge was first captured in `SESSION_LOG` or handoff for short-term continuity, promote it to the correct durable home before claiming it is long-term.
4. Add or update a QA check when the same failure class could recur and can be tested.
5. Keep governance bridge wording reserved for document orphan prevention. Do not relabel non-file governance as "file connected to Agent Handoff Kit".

Output format:

- Status: bridged / partially bridged / unbridged / blocked.
- Already bridged: list the governance links that are present.
- Gaps: list missing links and why they matter for the next agent.
- Suggested patches: list exact files and sections to update.
- Manual decisions: list duplicates, naming choices, deletion, renaming, external sync, or ownership questions requiring user confirmation.
- Acceptance: give one concrete check that proves the bridge is complete.

## Checks

- Verify affected files are indexed or intentionally installed templates.
- Check `dev/DOC_SYNC_REGISTRY.md` for governance, closeout/startup, and README sync rows.
- Confirm old overlapping wording was retired or marked legacy.
- Confirm any new durable file is reachable from `dev/PROJECT_INDEX.md` and does not rely only on a one-session handoff note.
- Confirm reusable operating procedure knowledge is not stored only in `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`, or a decision narrative when it belongs in a pack or registered reference.
- Confirm long-term governance knowledge is promoted out of `dev/SESSION_LOG.md`, `dev/SESSION_HANDOFF.md`, and `START_NEXT_SESSION_PROMPT.txt` when it should survive log archive or prompt regeneration.
- For governance bridge work, confirm the target file, project index, sync registry, related workflow, handoff/log role split, and duplicate-source risk were all checked or explicitly marked not applicable.
- Before claiming completion, apply the active root's core persistence gate and record the result only when that gate selects a checkpoint or full closeout; do not assume child or demo workspaces cover the parent/root workspace.
- For long-running projects, confirm `dev/PROJECT_DECISIONS.md` retains its four H2 sections in order (Evolution Timeline / Decisions Archive / Architecture Choices / Insights & Learnings) and that the closeout maintenance trigger check was recorded, with full maintenance applied where its trigger conditions were met.

## Closeout

Record the changed rule home, reason, complexity impact, retired wording, and follow-up checks.
