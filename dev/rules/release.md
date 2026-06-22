# Release Pack

## Scope

Use for release, publish, deploy, tag, version bump, hotfix, or GA completion claims.

## Load When

- User asks to publish, deploy, tag, release, upload, announce, or mark work as production-ready.
- A task changes package metadata, changelog, release notes, or distribution artifacts.

## Rules

1. Treat release claims as evidence-bound.
2. Verify version, target branch, commit, artifacts, release notes, and public docs before claiming completion.
3. Do not publish, deploy, tag, or upload without explicit user approval.
4. Keep rollback or recovery notes when release risk is non-trivial.
5. Preserve migration and upgrade safety for existing users.

## Checks

- Run build/test/package checks required by `dev/PROJECT_INDEX.md`.
- Check README, changelog, migration notes, and `dev/DOC_SYNC_REGISTRY.md`.
- Record exact command results or blockers.

## Closeout

Record release status, version, commit, artifacts, verification evidence, blocked items, and post-release follow-up.
