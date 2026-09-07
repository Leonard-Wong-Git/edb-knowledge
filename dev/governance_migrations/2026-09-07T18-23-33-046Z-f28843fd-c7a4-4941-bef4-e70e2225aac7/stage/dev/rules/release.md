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
6. If this candidate changes a public language counterpart, load the Writing Pack and require its independent semantic review for each changed source/target pair before release. Do not repeat that review for unchanged pairs; the candidate evidence records only the pairs this release changed.

## Checks

- Run build/test/package checks required by `dev/PROJECT_INDEX.md`.
- Check README, changelog, migration notes, and `dev/DOC_SYNC_REGISTRY.md`.
- When public bilingual material changed, check the candidate evidence identifies the changed pair, its source and target hashes after review, and the independent verdict. Do not substitute length, emoji, keyword, link, or an older PASS for that review.
- Record exact command results or blockers.

## Closeout

Record release status, version, commit, artifacts, verification evidence, blocked items, and post-release follow-up.
