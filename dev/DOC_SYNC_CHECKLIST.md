# Doc Sync Checklist
<!-- LOCAL PROJECT RECORD -->
<!--
  USAGE: At PERSIST phase, if any file was created or modified during CHANGE:
  1. Identify the change category in the registry below
  2. Execute all "Required Doc Updates" for matched rows
  3. Record triggered rows in SESSION_LOG under "Doc Sync"
  4. If your change type has no matching row: add the row first, then proceed
     (prevents this registry from going stale)
-->

## Change Category Registry

| Change Category | Required Doc Updates | Verification Method |
|---|---|---|
| Governance rule change (AGENTS.md) | INIT.md FILE 1 mirror; README if behavior is user-facing | grep parity check |
| Tech stack / build / dependency change | CODEBASE_CONTEXT.md Stack or Build section | manual review |
| External API / service change | CODEBASE_CONTEXT.md External Services block | block format check |
| New governance file added to install | §5a backup list in AGENTS.md; INIT.md ROOT SAFETY CHECK backup list; INIT.md FILE 1 §5a | grep check |
| New project doc added | This file — add a row for the new doc's update triggers | row presence check |
| Governance bootstrap / INIT execution | SESSION_HANDOFF.md Last Session Record; SESSION_LOG.md task entry + handoff prompt | manual review |
| Product behavior / tuning change | SESSION_HANDOFF.md baseline, priorities, risks if affected; SESSION_LOG.md task entry + QC evidence | manual review |
| Product version / release milestone change | k1-dashboard.html `_meta`; dev/knowledge/role_facts.json `_meta`; README badge; CHANGELOG; SESSION_HANDOFF.md; SESSION_LOG.md; CODEBASE_CONTEXT.md if release summary changed | manual review |
| Backend README / standalone runbook added | CODEBASE_CONTEXT.md Build & Run or Directory Map; SESSION_HANDOFF.md priorities if operator flow changes; SESSION_LOG.md task entry + QC evidence | manual review |
| _[Add project-specific rows below this line]_ | | |

## Anti-pattern: No Matching Row

If your change has no matching row above:
- Do NOT skip silently — add the missing row first, then proceed
- Record the registry addition in SESSION_LOG under `Doc Sync: registry updated`
- Reason: a stale registry is worse than no registry (false safety net)
