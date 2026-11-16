# Agent Handoff Kit Migration Report

- Transaction: 2026-11-16T22-38-39-618Z-928ab8c4-6127-498c-895d-a473b4daaef7
- Mode: upgrade-existing
- Attempted version: 0.4.7
- Committed version: 0.4.7
- Transaction state: committed
- Created at: 2026-11-16T22:38:39.628Z
- Committed at: 2026-11-16T22:38:40.177Z
- Credential values: not recorded

## Actions

- merge: AGENTS.md - update artifact-bound official v0.4.4 managed core with an explicit newline transform; preserve every surrounding byte; backup=dev/governance_migrations/2026-11-16T22-38-39-618Z-928ab8c4-6127-498c-895d-a473b4daaef7/backup/AGENTS.md; committed=true
- merge: dev/SESSION_HANDOFF.md - update handoff lifecycle/startup contracts while preserving current project state; backup=dev/governance_migrations/2026-11-16T22-38-39-618Z-928ab8c4-6127-498c-895d-a473b4daaef7/backup/dev/SESSION_HANDOFF.md; committed=true
- merge: dev/rules/safety.md - update artifact-bound official v0.4.3 dev/rules/safety.md rule body with an explicit newline transform; preserve local appendix bytes; backup=dev/governance_migrations/2026-11-16T22-38-39-618Z-928ab8c4-6127-498c-895d-a473b4daaef7/backup/dev/rules/safety.md; committed=true
- merge: dev/rules/coding.md - update artifact-bound official v0.4.3 dev/rules/coding.md rule body with an explicit newline transform; preserve local appendix bytes; backup=dev/governance_migrations/2026-11-16T22-38-39-618Z-928ab8c4-6127-498c-895d-a473b4daaef7/backup/dev/rules/coding.md; committed=true
- merge: dev/rules/closeout.md - update artifact-bound official v0.4.4 dev/rules/closeout.md rule body with an explicit newline transform; preserve local appendix bytes; backup=dev/governance_migrations/2026-11-16T22-38-39-618Z-928ab8c4-6127-498c-895d-a473b4daaef7/backup/dev/rules/closeout.md; committed=true
- merge: dev/rules/integrations.md - update artifact-bound official v0.4.4 dev/rules/integrations.md rule body with an explicit newline transform; preserve local appendix bytes; backup=dev/governance_migrations/2026-11-16T22-38-39-618Z-928ab8c4-6127-498c-895d-a473b4daaef7/backup/dev/rules/integrations.md; committed=true
- merge: dev/handoff-kit/assets.mjs - verified official v0.4.3 shortcut update; backup=dev/governance_migrations/2026-11-16T22-38-39-618Z-928ab8c4-6127-498c-895d-a473b4daaef7/backup/dev/handoff-kit/assets.mjs; committed=true
- merge: dev/PROJECT_INDEX.md - update only the unique real PROJECT_INDEX Stack template-version row while preserving every other PROJECT_INDEX byte; backup=dev/governance_migrations/2026-11-16T22-38-39-618Z-928ab8c4-6127-498c-895d-a473b4daaef7/backup/dev/PROJECT_INDEX.md; committed=true
- merge: START_NEXT_SESSION_PROMPT.txt - regenerated from authoritative handoff opening message; backup=dev/governance_migrations/2026-11-16T22-38-39-618Z-928ab8c4-6127-498c-895d-a473b4daaef7/backup/START_NEXT_SESSION_PROMPT.txt; committed=true

- Planned skips: 58
- Conflicts: 0

## Formal User Rules Acceptance
- not applicable

## Historical Authority
- Completed transaction journals are operation receipts only after their lock is cleared.
- Future doctor and upgrade runs validate current contracts rather than this receipt.
