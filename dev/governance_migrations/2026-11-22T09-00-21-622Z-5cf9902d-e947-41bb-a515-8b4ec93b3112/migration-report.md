# Agent Handoff Kit Migration Report

- Transaction: 2026-11-22T09-00-21-622Z-5cf9902d-e947-41bb-a515-8b4ec93b3112
- Mode: upgrade-existing
- Attempted version: 0.4.8
- Committed version: 0.4.8
- Transaction state: committed
- Created at: 2026-11-22T09:00:21.632Z
- Committed at: 2026-11-22T09:00:23.149Z
- Credential values: not recorded

## Actions

- merge: dev/rules/coding.md - update artifact-bound official v0.4.7 dev/rules/coding.md rule body with an explicit newline transform; preserve local appendix bytes; backup=dev/governance_migrations/2026-11-22T09-00-21-622Z-5cf9902d-e947-41bb-a515-8b4ec93b3112/backup/dev/rules/coding.md; committed=true
- merge: dev/rules/closeout.md - update artifact-bound official v0.4.7 dev/rules/closeout.md rule body with an explicit newline transform; preserve local appendix bytes; backup=dev/governance_migrations/2026-11-22T09-00-21-622Z-5cf9902d-e947-41bb-a515-8b4ec93b3112/backup/dev/rules/closeout.md; committed=true
- merge: dev/handoff-kit/assets.mjs - verified official v0.4.7 shortcut update; backup=dev/governance_migrations/2026-11-22T09-00-21-622Z-5cf9902d-e947-41bb-a515-8b4ec93b3112/backup/dev/handoff-kit/assets.mjs; committed=true
- merge: dev/PROJECT_INDEX.md - update only the unique real PROJECT_INDEX Stack template-version row while preserving every other PROJECT_INDEX byte; backup=dev/governance_migrations/2026-11-22T09-00-21-622Z-5cf9902d-e947-41bb-a515-8b4ec93b3112/backup/dev/PROJECT_INDEX.md; committed=true
- merge: START_NEXT_SESSION_PROMPT.txt - regenerated from authoritative handoff opening message; backup=dev/governance_migrations/2026-11-22T09-00-21-622Z-5cf9902d-e947-41bb-a515-8b4ec93b3112/backup/START_NEXT_SESSION_PROMPT.txt; committed=true

- Planned skips: 62
- Conflicts: 0

## Formal User Rules Acceptance
- not applicable

## Historical Authority
- Completed transaction journals are operation receipts only after their lock is cleared.
- Future doctor and upgrade runs validate current contracts rather than this receipt.
