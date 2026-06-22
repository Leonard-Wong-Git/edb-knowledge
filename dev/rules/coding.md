# Coding Pack

## Scope

Use for code changes, tests, builds, package managers, SDKs, CLIs, APIs, or developer tooling.

## Load When

- User asks to write, edit, debug, refactor, test, build, package, or integrate code.
- The task depends on framework, runtime, dependency, or API behavior.

## Rules

1. Read `dev/PROJECT_INDEX.md` for stack, commands, entry points, and directory roles before editing.
2. Inspect relevant source, tests, configs, and docs before changing code.
3. Prefer project-local patterns and helpers over new abstractions.
4. Do not guess current SDK, CLI, package, API, or deployment behavior when docs or project files can verify it.
5. Preserve unrelated user changes.

## Checks

- Run the narrowest relevant test, build, lint, or typecheck available.
- If a check cannot run, record why and what remains unverified.
- Check `dev/DOC_SYNC_REGISTRY.md` if behavior, commands, public docs, or runbooks changed.

## Closeout

Record files changed, commands run, results, remaining risks, and any project index or doc sync updates.
