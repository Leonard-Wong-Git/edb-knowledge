# Safety Pack

## Scope

Use for file operations, shell commands, Git changes, package managers, installers, deploy tools, release tools, cloud tools, external APIs, locked files, permission errors, sandbox restrictions, or any task that could affect data loss, credentials, public release state, or external systems.

## Load When

- User requests deletion, overwrite, move, rename, cleanup, Git history changes, package installation, publish, deploy, release, cloud writes, external API calls, or credential handling.
- A task touches filesystem paths, shell commands, permissions, sandbox limits, locks, secrets, external systems, or public release state.
- Another pack is loaded but the task includes data-loss, credential, permission, external-system, or irreversible-operation risk.

## Rules

1. Before deleting, overwriting, moving, renaming, cleaning, resetting, publishing, or running destructive tool operations, list the exact target paths, expected scope, impact, and required confirmation.
2. Preserve user-provided source files by default. Create renamed outputs instead of in-place overwrites unless overwrite is explicitly requested.
3. Never operate on a filesystem root, drive root, home directory root, repository parent root, system directory, or ambiguous path.
4. Do not bypass permissions, file locks, sandbox limits, failed safety checks, or denied operations. Report the blocker and manual action needed.
5. Do not run recursive or bulk destructive commands such as `rm -rf`, `Remove-Item -Recurse -Force`, `git clean -fdx`, or equivalent cleanup operations unless the user explicitly requested the operation and resolved absolute targets are verified.
6. On Windows, do not use `cmd /c rmdir`, `cmd /c rd`, or any `cmd.exe /c` variant combined with `rmdir` or `rd`. Prefer native PowerShell cmdlets when PowerShell is active, and do not compose filesystem modification commands across shells.
7. On macOS / Linux, do not run `rm -rf`, `sudo rm`, recursive `chmod`, recursive `chown`, or destructive wildcard operations unless the user explicitly requested the operation and target paths are listed and verified.
8. Do not run `git reset --hard`, branch deletion, tag deletion, force push, or history rewrite unless the user explicitly requested it and affected refs/files are listed.
9. Before staging or committing, inspect current status and avoid staging unrelated parent-repo, sibling-directory, generated, credential, or user-owned changes.
10. Before using external APIs, SDKs, CLIs, package managers, deploy tools, cloud tools, or release tools, verify current official documentation or project-local runbooks. Differentiate three layers of external access (R-030 Integration governance; see `dev/rules/integrations.md`):
   (a) Anthropic-vetted Connectors (e.g. Notion / Google Drive / Slack via Claude Desktop Extensions): trust the vetted MCP server behavior; still verify destructive write parameters before invocation.
   (b) Community / custom MCP servers (user-installed via manual config): treat with extra caution — destructive writes require dry-run + user confirmation; verify server behavior against project-local runbook if available.
   (c) Raw external APIs / SDKs / CLIs (no MCP layer): full Rule 10 verification of official docs required; mark unverified if blocked.
11. Do not print, copy, log, commit, upload, or generate files containing secret values. Use redacted placeholders or line references.
12. Credential leak prevention (R-030 Integration governance):
   (a) Never request, log, or persist credential values (API keys / OAuth tokens / app secrets / refresh tokens) in any project file. Credentials live exclusively in AI tool secure storage (OS Keychain / Credential Manager / AI tool config) or env vars, never in `dev/*`.
   (b) Recognize common credential prefixes (`sk-`, `sk-ant-`, `ntn_`, `secret_`, `ya29.`, `1//`, `xoxp-`, `xoxb-`, `ghp_`, `gho_`, `ghs_`, `github_pat_`, `sl.`, `AKIA`, `AIza`) — if a value matching any prefix appears in conversation, redact immediately and warn the user to rotate the token.
   (c) Before writing to `dev/PROJECT_INDEX.md` `## Installed Integrations`, `dev/SESSION_HANDOFF.md`, or `dev/SESSION_LOG.md`, self-check that no credential value is present; doctor `checkInstalledIntegrationsCredentialLeak()` enforces this at QC.
   (d) Auth failure (token expired / revoked / rate-limit) surfaces to the user with a pointer to the AI tool's own settings interface; do not attempt to auto-fix auth or re-auth flow (out of scope for Kit governance).

## Checks

- Report which safety-relevant command, path, API, install, deploy, release, or Git check was performed and the result.
- If checks cannot run, state the reason and mark the result unverified.
- For durable governance changes, update the project index, sync registry, and any human review map if they exist.

## Closeout

Record unresolved safety risks, blocked verification, pending manual actions, dirty worktrees, or external sync gaps in `dev/SESSION_HANDOFF.md`.
