# Agent Handoff Kit Migration Report

- Transaction: 2026-09-07T18-23-33-046Z-f28843fd-c7a4-4941-bef4-e70e2225aac7
- Mode: upgrade-existing
- Attempted version: 0.3.66
- Committed version: 0.3.66
- Transaction state: committed
- Created at: 2026-09-07T18:23:33.054Z
- Committed at: 2026-09-07T18:23:34.001Z
- Credential values: not recorded

## Actions

- merge: AGENTS.md - update artifact-bound official v0.3.29 managed core with an explicit newline transform; preserve every surrounding byte; backup=dev/governance_migrations/2026-09-07T18-23-33-046Z-f28843fd-c7a4-4941-bef4-e70e2225aac7/backup/AGENTS.md; committed=true
- merge: dev/SESSION_HANDOFF.md - update handoff lifecycle/startup contracts while preserving current project state; backup=dev/governance_migrations/2026-09-07T18-23-33-046Z-f28843fd-c7a4-4941-bef4-e70e2225aac7/backup/dev/SESSION_HANDOFF.md; committed=true
- merge: dev/PROJECT_INDEX.md - insert the missing Installed Integrations and Tool Operation References H2 sections while preserving all existing project content; backup=dev/governance_migrations/2026-09-07T18-23-33-046Z-f28843fd-c7a4-4941-bef4-e70e2225aac7/backup/dev/PROJECT_INDEX.md; committed=true
- merge: dev/DOC_SYNC_REGISTRY.md - replace raw-exact official historical dev/DOC_SYNC_REGISTRY.md with the current Kit file; backup=dev/governance_migrations/2026-09-07T18-23-33-046Z-f28843fd-c7a4-4941-bef4-e70e2225aac7/backup/dev/DOC_SYNC_REGISTRY.md; committed=true
- merge: dev/RULE_PACKS.md - update marker-identified official routing rows while preserving every unmarked local row; backup=dev/governance_migrations/2026-09-07T18-23-33-046Z-f28843fd-c7a4-4941-bef4-e70e2225aac7/backup/dev/RULE_PACKS.md; committed=true
- merge: dev/PROJECT_DECISIONS.md - restore PROJECT_DECISIONS onboarding preamble before ## Evolution Timeline; backup=dev/governance_migrations/2026-09-07T18-23-33-046Z-f28843fd-c7a4-4941-bef4-e70e2225aac7/backup/dev/PROJECT_DECISIONS.md; committed=true
- merge: dev/rules/safety.md - update artifact-bound official v0.3.30 dev/rules/safety.md rule body with an explicit newline transform; preserve local appendix bytes; backup=dev/governance_migrations/2026-09-07T18-23-33-046Z-f28843fd-c7a4-4941-bef4-e70e2225aac7/backup/dev/rules/safety.md; committed=true
- merge: dev/rules/writing.md - update artifact-bound official v0.3.29 dev/rules/writing.md rule body with an explicit newline transform; preserve local appendix bytes; backup=dev/governance_migrations/2026-09-07T18-23-33-046Z-f28843fd-c7a4-4941-bef4-e70e2225aac7/backup/dev/rules/writing.md; committed=true
- merge: dev/rules/agent-governance.md - update artifact-bound official v0.3.29 dev/rules/agent-governance.md rule body with an explicit newline transform; preserve local appendix bytes; backup=dev/governance_migrations/2026-09-07T18-23-33-046Z-f28843fd-c7a4-4941-bef4-e70e2225aac7/backup/dev/rules/agent-governance.md; committed=true
- merge: dev/rules/release.md - update artifact-bound official v0.3.43 dev/rules/release.md rule body with an explicit newline transform; preserve local appendix bytes; backup=dev/governance_migrations/2026-09-07T18-23-33-046Z-f28843fd-c7a4-4941-bef4-e70e2225aac7/backup/dev/rules/release.md; committed=true
- merge: dev/rules/knowledge.md - update artifact-bound official v0.3.32 dev/rules/knowledge.md rule body with an explicit newline transform; preserve local appendix bytes; backup=dev/governance_migrations/2026-09-07T18-23-33-046Z-f28843fd-c7a4-4941-bef4-e70e2225aac7/backup/dev/rules/knowledge.md; committed=true
- create: dev/rules/closeout.md - create; backup=none; committed=true
- merge: dev/rules/onboarding.md - update artifact-bound official v0.3.32 dev/rules/onboarding.md rule body with an explicit newline transform; preserve local appendix bytes; backup=dev/governance_migrations/2026-09-07T18-23-33-046Z-f28843fd-c7a4-4941-bef4-e70e2225aac7/backup/dev/rules/onboarding.md; committed=true
- merge: dev/rules/integrations.md - update artifact-bound official v0.3.32 dev/rules/integrations.md rule body with an explicit newline transform; preserve local appendix bytes; backup=dev/governance_migrations/2026-09-07T18-23-33-046Z-f28843fd-c7a4-4941-bef4-e70e2225aac7/backup/dev/rules/integrations.md; committed=true
- merge: START_NEXT_SESSION_PROMPT.txt - regenerated from authoritative handoff opening message; backup=dev/governance_migrations/2026-09-07T18-23-33-046Z-f28843fd-c7a4-4941-bef4-e70e2225aac7/backup/START_NEXT_SESSION_PROMPT.txt; committed=true

- Planned skips: 8
- Conflicts: 0

## Formal User Rules Acceptance
- not applicable

## Historical Authority
- Completed transaction journals are operation receipts only after their lock is cleared.
- Future doctor and upgrade runs validate current contracts rather than this receipt.
