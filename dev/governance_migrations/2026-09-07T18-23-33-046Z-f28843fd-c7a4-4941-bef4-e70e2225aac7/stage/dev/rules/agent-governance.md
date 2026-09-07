# Agent Governance Pack

## Scope

Use for governance rules, prompts, agent instructions, handoff systems, startup/closeout behavior, skills, and rule packs.

## Load When

- User asks to change AI behavior, project governance, prompts, handoff, startup, closeout, or tool-use rules.
- A change affects `AGENTS.md`, `dev/*`, rule packs, installer templates, or durable workflow docs.
- User asks to bridge governance, connect a document to governance, scan for unbridged governance documents, or uses equivalent Chinese phrases such as "治理打通", "把文件接入 Agent Handoff Kit", "接入 Agent Handoff Kit", or "掃描未接入 Agent Handoff Kit 的重要文件".
- User asks to make something long-term, cross-session, reusable, future sessions should remember an API / MCP / tool-use pattern, or uses equivalent Chinese phrases such as "寫入長期治理", "轉成長期機制", or "之後都要遵守".
- The task creates or materially changes Markdown governance artifacts, source-of-truth files, durable workflow docs, or durable artifacts that future agents may need to discover. Ordinary target-authority documents, drafts, and user-task deliverables do not load this pack solely because they are Markdown or generated.

## Rules

1. Locate the existing source of truth before adding a rule. Read the matching categories in `dev/RULE_PACKS.md`, their applicable packs, project supplements and required references first; then apply `Governance Write Boundary` below. A matching topic does not make official prose writable.
2. Prefer merge, replace, or registry rows over append-only rule growth, within the verified project-owned location. Change an existing project rule in place rather than duplicating it in another file or appending an override.
3. Keep public runtime rules generic; project-specific incidents belong in logs, runbooks, or project index.
4. Do not let development-only workspace rules enter public runtime.
5. Check complexity budget before adding default-core behavior.
6. Before creating durable workflow, runbook, or instruction files, first classify the knowledge type and verify whether an existing home can carry it without a new file: current state belongs in `dev/SESSION_HANDOFF.md`; trace evidence belongs in `dev/SESSION_LOG.md`; file / command / reference maps belong in `dev/PROJECT_INDEX.md`; sync obligations belong in `dev/DOC_SYNC_REGISTRY.md`; reusable operating procedures belong in the relevant rule pack or registered reference. New runbooks are last resort only.
7. When a task uses external skills, subagents, demo workspaces, or another tool's closeout, treat those flows as subordinate to the active root's Agent Handoff Kit governance. The active root still needs the `runtime-core/AGENTS.core.md` persistence gate decision; do not duplicate the gate thresholds in this pack.
8. Before any pre-closeout handoff / log write for governance work, apply the core Persistence Gate explicitly. A concern that future agents may read stale handoff is not enough when the changed rule, spec, runbook, or document is itself the target authority; leave handoff lag expected unless checkpoint conditions are met. When the gate does select a checkpoint, write only the smallest current-state field or concise log entry and leave historical evidence sections byte-stable where practical.
9. For long-running projects, maintain `dev/PROJECT_DECISIONS.md` per R-028 closeout discipline (see `runtime-core/AGENTS.core.md` closeout maintenance trigger check): capture major decisions when they happen, run the short trigger check at every closeout, and do full long-term maintenance only when a hard trigger, semantic trigger, or 10-closeout backstop applies. Short single-task projects keep this as a no-op default; users are not expected to edit this file manually.
10. Governance bridge is a triggered review, not a default startup scan. Use it when an important file, source-of-truth document, runbook, production guide, workflow, checklist, stock list, or similar durable document may need to be connected to project governance.
11. Content-based trigger: long-term governance routing is content-based, not trigger-only. Even if the user does not use explicit governance-routing phrases, treat a statement as durable governance when it says future sessions must follow it, when it corrects a recurring AI mistake, or when it defines a reusable API / MCP / tool-use pattern. Do not persist long-term governance knowledge only in `dev/SESSION_LOG.md`, `dev/SESSION_HANDOFF.md`, or `START_NEXT_SESSION_PROMPT.txt`; those surfaces may be compressed, archived, or regenerated.
12. Mid-task changes to product goals, requirements, development checklists, acceptance rules, exclusions, priorities, or scope are task contract changes. Before writing them, check whether the same contract already lives in a spec, backlog, issue list, README, runbook, project index entry, or handoff section. Merge into the existing authoritative home, then leave only a pointer or current-state summary elsewhere.
13. New Markdown or generated documents are not automatically harmless. After creating or materially changing them, classify each artifact before completion: source of truth, reference, runbook, workflow, checklist, public document, generated output, one-time evidence, draft, or temporary. Durable artifacts must be discoverable from `dev/PROJECT_INDEX.md` or intentionally tied to a registered sync / source-of-truth row. Temporary or one-time evidence must be labeled as such in the task record or closeout so future agents do not treat it as hidden current state.
14. Do not create a new document to hold a rule, requirement, checklist, or process if an existing authoritative document can carry it. Merge into the existing home or make the new document explicitly subordinate. If two files now carry the same durable instruction, resolve the duplicate by choosing one authoritative home and pointing the other to it.

## Governance Write Boundary

This is the single write-location contract for installed projects, not for authorized Kit source development. It guides agent edits; it cannot intercept arbitrary editor writes.

1. Classify the change before writing. Use the existing task category and normative owner; read the full relevant rule and its project supplements. A current task instruction is not automatically a durable rule. Do not create a new goal, acceptance threshold or balancing policy merely to reconcile your preferences with the user's request. Follow instruction priority; surface a material unresolved conflict instead of silently inventing an override.
2. Treat the `AGENTS.md` managed-core region and complete official `dev/rules/*` pack bodies as protected. Daily project edits must not insert, translate, reformat, reorder or remove their contents or delimiters. Verify the installed version's official content before identifying the boundary; a heading, marker or version row alone is not ownership proof. Formal upgrade or an explicitly scoped repair owns official changes. If local rules are already interleaved, preserve them and report the required bounded reconciliation; do not guess which lines to delete or bless the mixed body as official.
3. Reuse the matching pack's existing project supplement when it owns the rule. Otherwise place a short local rule after the entire verified official body under `## Project Rules`; preserve the official trailing newline. This heading labels the writable appendix, not the end of official ownership. For substantial or shared procedures, reuse a registered project reference; create a new reference only if no suitable owner exists. If `dev/USER_RULES.md` formally owns the rule, use its accepted update procedure rather than editing witnessed bytes or creating a competing copy. Always-needed project entry rules may live outside the managed core only after checking their existing owner.
4. Preserve project-state schemas separately: edit handoff fields, actual log entries, index data or registry rows in their existing writable sections; do not insert policy into template instructions or alter machine markers. Preserve official routing rows in `dev/RULE_PACKS.md`; add a project row only when a project reference needs a task trigger, naming both the relevant pack and reference. A same-pack appendix uses that pack's existing route. Do not add a route or load a pack merely for bare startup.
5. Before and after an edit touching core or pack files, compare the complete protected region against the verified input; every protected byte must remain unchanged. Use the installed-version CLI's read-only `upgrade --dry-run --root <project root>` before and after those edits as the compatibility check; record the CLI version and any existing conflict separately. A pre-existing conflict requires reconciliation before claiming the write boundary is verified. A new conflict or changed official region prevents completion; restore only your own scoped change from its verified input without discarding concurrent or pre-existing user work. For ordinary project-state edits, use schema/marker and local readback checks instead of an upgrade preview.
6. Read back the rule from its normal consumer path: task signal -> router -> relevant pack including the project supplement and required reference -> requested action. Verify its exact requirement, scope and precedence, and that unrelated packs stay unloaded. An indexed file that no applicable route reads is not connected. Evidence must show both correct application and preserved upgrade compatibility; a successful preview alone does not prove an AI followed the rule.

## Governance Bridge Workflow

Use this workflow when the user asks for governance bridge, connect this document to governance, asks to scan for unbridged governance documents, or uses equivalent Chinese phrases such as "治理打通", "把文件接入 Agent Handoff Kit", "接入 Agent Handoff Kit", or "掃描未接入 Agent Handoff Kit 的重要文件".

1. Identify the target. If the user named a file, inspect that file and its surrounding directory. If no file is named, run a bounded repo scan for likely durable documents such as source-of-truth files, runbooks, workflows, guides, checklists, stock lists, production guides, and rules.
2. Check the target file itself: it should state its role, scope, update trigger, owner or responsible workflow when known, and what must not be inferred from it.
3. Check `dev/PROJECT_INDEX.md`: the file should be discoverable with its role and "read when" condition. Source-of-truth or reference files should appear in Fact Base, External Sources, Directory Map, Entry Points, or another existing indexed home that fits the project.
4. Check `dev/DOC_SYNC_REGISTRY.md`: future same-type changes should have a matching change type or an explicit reason no durable sync rule is needed.
5. Check related workflows, guides, runbooks, or rule packs: if a process creates or updates the file, that process should say when to update the file or its index row.
6. Check `dev/SESSION_HANDOFF.md`: only current state, recommended next action with reason, unresolved risk, blocker, or a startup-needed fact should be in handoff. Do not copy whole documents or old evidence into handoff.
7. Check `dev/SESSION_LOG.md`: this session's bridge review, validation, and evidence can be logged when it affects future action, but log entries must not become current state.
8. Search for duplicate source-of-truth risk. If another file has the same durable role, recommend merge, reference, or retire options; do not delete, rename, or move files without explicit approval.

For repo-wide scans, report candidates as candidates. Do not fail ordinary docs merely because they are not indexed; only durable files that future agents need to discover, update, or distinguish from drafts should be bridged.

Output format:

- Status: bridged / partially bridged / unbridged / blocked.
- Use bridged only when every applicable governance link is present. If only `dev/PROJECT_INDEX.md` or `dev/SESSION_LOG.md` was updated, report partially bridged.
- Already bridged: list the governance links that are present.
- Gaps: list missing links and why they matter for the next agent.
- Not applicable: list skipped layers with a reason.
- Suggested patches: list exact files and sections to update.
- Manual decisions: list duplicates, naming choices, deletion, renaming, external sync, or ownership questions requiring user confirmation.
- Acceptance: give one concrete check that proves the bridge is complete.

## Generated Artifact Governance Workflow

Use this workflow whenever the current task creates or materially changes Markdown documents or other durable artifacts, even if the user did not explicitly ask for governance bridge.

This workflow is subordinate to the core task-first governance locality rule. Use it as a proportionate classification / routing check, not as permission to interrupt an explicit user task plan, start a repo-wide governance scan, or turn an ordinary user-task deliverable into governance work.

1. List the artifacts created or materially changed in this task.
2. Classify each artifact: source of truth, reference, runbook, workflow, checklist, public document, generated output, one-time evidence, draft, or temporary.
3. For source-of-truth, reference, runbook, workflow, checklist, public document, and reusable generated output, update `dev/PROJECT_INDEX.md` so the file is discoverable with a role and read condition.
4. For artifacts that require future mirror, external index, publication, or repeated sync, update `dev/DOC_SYNC_REGISTRY.md` or record why no durable sync rule applies.
5. For one-time evidence, draft, or temporary files, record that classification in `dev/SESSION_LOG.md` or the task summary, and do not promote it to current handoff unless it affects the next action.
6. Search for duplicate source-of-truth risk before keeping a new document. If another file already owns the same rule, requirement, checklist, or process, merge into that file or make the new document explicitly subordinate.
7. Before claiming completion, explicitly confirm the artifacts created or materially changed in this task have been classified, indexed, synchronized, consolidated, or marked temporary through the steps above. Existing target-authority documents that only received a local content edit normally need read-back and task-specific validation, not a handoff / log write or a bundled doctor run. You may run the available project governance check and `agent-handoff-kit doctor` only for scoped Kit / typed registered-surface checks; doctor does not discover unregistered ordinary workspace files and cannot replace explicit changed-artifact review.

## Long-term Governance Routing

Use this workflow when the user asks to write something into long-term governance, turn an experience into a mechanism, make a rule apply across sessions, or when the content itself clearly has durable force.

1. Classify the knowledge before writing:
   - Current task contract changes, including product goals, requirements, development checklists, acceptance rules, exclusions, priorities, or scope -> the existing authoritative spec / backlog / issue / runbook when one exists; otherwise `dev/SESSION_HANDOFF.md` current-state sections.
   - Current task state, recommended next action with reason, unresolved risk, or startup-needed fact -> `dev/SESSION_HANDOFF.md`.
   - Chronological evidence or validation trace -> `dev/SESSION_LOG.md`.
   - File maps, command maps, API reference locations, tool capability maps, and external source coordinates -> `dev/PROJECT_INDEX.md`.
   - Sync obligations or external mirror duties -> `dev/DOC_SYNC_REGISTRY.md`.
   - Durable decisions, architecture trade-offs, research-derived rationale, and long-term lessons -> `dev/PROJECT_DECISIONS.md`.
   - Reusable procedures, recurring mistake prevention, API / MCP / tool-use rules -> the relevant rule pack, registered reference, or QA check.
   - API / MCP / tool-use patterns -> project index / registered reference / integrations pack, depending on scope.
2. If the knowledge is reusable but no existing home fits, propose the smallest new registered reference or rule-pack patch. New runbooks remain last resort.
3. If the knowledge was first captured in `SESSION_LOG` or handoff for short-term continuity, promote it to the correct durable home before claiming it is long-term.
4. Add or update a QA check when the same failure class could recur and can be tested.
5. Repeat-failure escalation: when the same failure class recurs after an AI has already claimed a durable fix for that class, do not continue with another same-pattern patch as ordinary work. Limit the escalation to the affected domain: identify the authoritative owner, correct or remove the failed method there, add a counterexample or replay check that would have failed before the fix when feasible, and state the temporary constraint. If the failure recurs again after that root-fix validation, separate the change and validation roles where the runtime provides an independent reviewer, subagent, or fresh-context pass; when none is available, perform a fresh read-back pass against the replay check and mark independent review unavailable instead of blocking unrelated work. Restore normal flow as soon as the replay and review / read-back pass. Do not create a central penalty database, cross-project blacklist, permanent role split, or public rule carrying project-specific incident details.
6. Keep governance bridge wording reserved for document orphan prevention. Do not relabel non-file governance as "file connected to Agent Handoff Kit".

## Checks

- Verify affected files are indexed or intentionally installed templates.
- Check `dev/DOC_SYNC_REGISTRY.md` for governance, closeout/startup, and README sync rows.
- Confirm old overlapping wording was retired or marked legacy.
- Confirm any new durable file is reachable from `dev/PROJECT_INDEX.md` and does not rely only on a one-session handoff note.
- Confirm every Markdown document or generated artifact created in this task is indexed, synced, consolidated, or explicitly classified as draft / temporary / one-time evidence.
- Confirm no new file has become a parallel source for an existing rule, requirement, checklist, or process.
- Confirm reusable operating procedure knowledge is not stored only in `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`, or a decision narrative when it belongs in a pack or registered reference.
- Confirm long-term governance knowledge is promoted out of `dev/SESSION_LOG.md`, `dev/SESSION_HANDOFF.md`, and `START_NEXT_SESSION_PROMPT.txt` when it should survive log archive or prompt regeneration.
- Confirm repeat-failure escalation, when triggered, is limited to the affected domain, tied to the authoritative owner, backed by a counterexample or replay check when feasible, and does not create a central penalty store, cross-project blacklist, or permanent role split.
- For governance bridge work, confirm the target file, project index, sync registry, related workflow, handoff/log role split, and duplicate-source risk were all checked or explicitly marked not applicable.
- For governance bridge work, run bounded searches for the target path/name and the relevant artifact class or sync-change type across the project index, sync registry, related workflows, and current rule owners. If the target is tied to generated outputs, also inspect the workflow or production guide that creates those outputs. Search evidence is a check, not a second source of truth.
- Before claiming completion, apply the active root's core persistence gate and record the result only when that gate selects a checkpoint or full closeout; do not assume child or demo workspaces cover the parent/root workspace.
- For long-running projects, confirm `dev/PROJECT_DECISIONS.md` retains its four H2 sections in order (Evolution Timeline / Decisions Archive / Architecture Choices / Insights & Learnings) and that the closeout maintenance trigger check was recorded, with full maintenance applied where its trigger conditions were met.

## Closeout

Record the changed rule home, reason, complexity impact, retired wording, and follow-up checks.
