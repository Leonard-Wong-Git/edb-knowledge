# Safety Pack

## Scope

Use for file operations, shell commands, Git changes, package managers, installers, deploy tools, release tools, cloud tools, external APIs, browser profiles, desktop app sessions, notebook kernels, local tool servers, locked files, permission errors, sandbox restrictions, or any task that could affect data loss, credentials, public release state, user sessions, shared local resources, or external systems.

## Load When

- User requests deletion, overwrite, move, rename, cleanup, Git history changes, package installation, publish, deploy, release, cloud writes, external API calls, or credential handling.
- A task touches filesystem paths, shell commands, permissions, sandbox limits, locks, secrets, external systems, browser profiles, desktop app sessions, notebook kernels, local tool servers, shared caches, or public release state.
- Another pack is loaded but the task includes data-loss, credential, permission, external-system, or irreversible-operation risk.

## Rules

1. Before deleting, overwriting, moving, renaming, cleaning, resetting, publishing, or running destructive tool operations, list the exact target paths, expected scope, impact, and required confirmation.
2. Preserve user-provided source files by default. Create renamed outputs instead of in-place overwrites unless overwrite is explicitly requested.
3. Never operate on a filesystem root, drive root, home directory root, repository parent root, system directory, or ambiguous path.
4. Do not bypass permissions, file locks, sandbox limits, failed safety checks, or denied operations. Report the blocker and manual action needed.
5. Never run `rm -rf`, `sudo rm -rf`, `Remove-Item -Recurse -Force`, `git clean -fdx`, `git reset --hard`, or an obfuscated / wrapped equivalent. User request does not make these named commands permissible. Use a narrower reversible operation or provide a manual action list.
6. On Windows, do not use `cmd /c rmdir`, `cmd /c rd`, or any `cmd.exe /c` variant combined with `rmdir` or `rd`. Prefer native PowerShell cmdlets when PowerShell is active, and do not compose filesystem modification commands across shells.
7. On macOS / Linux, never use destructive wildcards, recursive `chmod 777`, recursive `chown`, disk formatting, mount-point cleanup, or home/system-directory cleanup. Other destructive operations require explicit authorization plus resolved target verification and must use the narrowest safe tool.
8. Branch deletion, tag deletion, force push, and history rewrite require separate explicit authorization and affected-ref verification. The absolute prohibitions in Rule 5 remain prohibited even when such authorization exists.
9. Before staging or committing, inspect current status and avoid staging unrelated parent-repo, sibling-directory, generated, credential, or user-owned changes.
10. Before using external APIs, SDKs, CLIs, package managers, deploy tools, cloud tools, release tools, browser automation, DevTools, Playwright, crawlers, notebooks, desktop app automation, or local helper services, verify current official documentation or project-local runbooks. For external tools, first apply the External Tool Usage Verification Gate in `dev/rules/integrations.md`: inspect current runtime tool schema for Connector / MCP calls, and use current official docs, official type definitions, official samples, or registered tool operation references for raw API / SDK / CLI / URI / plugin API work. Differentiate three layers of external access:
   (a) Anthropic-vetted Connectors (e.g. Notion / Google Drive / Slack via Claude Desktop Extensions): trust the vetted MCP server boundary only after inspecting the active runtime tool name, description, and input schema; still verify destructive write parameters before invocation.
   (b) Community / custom MCP servers (user-installed via manual config): treat with extra caution — destructive writes require dry-run + user confirmation; verify server behavior against current tool schema and project-local runbook if available.
   (c) Raw external APIs / SDKs / CLIs (no MCP layer): full Rule 10 verification of official docs required; mark unverified if blocked.
11. Do not print, copy, log, commit, upload, or generate files containing secret values. Use redacted placeholders or line references.
12. Credential leak prevention (R-030 Integration governance):
   (a) Never request, log, or persist credential values (API keys / OAuth tokens / app secrets / refresh tokens) in any project file. Credentials live exclusively in AI tool secure storage, OS credential stores, AI tool config, user-managed secret stores, or env indirection; if env is used, project files may record only the env var name, never the value.
   (b) Recognize common credential prefixes (`sk-`, `sk-ant-`, `ntn_`, `secret_`, `ya29.`, `1//`, `xoxp-`, `xoxb-`, `ghp_`, `gho_`, `ghs_`, `github_pat_`, `sl.`, `AKIA`, `AIza`) — if a value matching any prefix appears in conversation, redact immediately and warn the user to rotate the token.
   (c) Before writing to `dev/PROJECT_INDEX.md` `## Installed Integrations`, `dev/SESSION_HANDOFF.md`, or `dev/SESSION_LOG.md`, self-check that no credential value is present; doctor `checkInstalledIntegrationsCredentialLeak()` enforces this at QC.
   (d) Auth failure (token expired / revoked / rate-limit) surfaces to the user with a pointer to the AI tool's own settings interface; do not attempt to auto-fix auth or re-auth flow (out of scope for Kit governance).
13. Shell / script parser failure discipline: after a shell, quoting, here-string, wrapper, temporary script, or parser failure, stop same-pattern retries and classify the failing layer before trying again: active shell, wrapper shell, runtime parser, package manager, or target CLI. Do not embed large JavaScript, JSON, Markdown, regex, patch, or path-heavy content inside shell strings when a direct tool, patch file, or real script file is safer. For temporary scripts, first make a minimal reproducible script, run a syntax-only check such as `node --check`, `python -m py_compile`, or an equivalent parser check where available, then execute. After any write script, read back the affected files or affected ranges before claiming success. If the same parser failure repeats, stop and return to root-cause classification instead of changing quoting again.
14. Process termination and cache cleanup boundary: agents may automatically close or clean up resources that are clearly task-owned or agent-managed, including task-created browser contexts, MCP child processes, helper servers, notebook kernels, temp directories, or bounded caches. Agents must not terminate shared, ambiguous, user-owned, system-level, or other-agent-owned processes; delete broad caches; disable tools; uninstall packages; mutate browser profiles, desktop app sessions, shared tool servers, notebook kernels, global package / browser / plugin caches, or change configuration without explicit user confirmation listing exact process IDs or paths, tool names, evidence, expected impact, and restart / rollback path. Generic process names such as `node`, `python`, or `chrome` are never enough ownership evidence by themselves. If a process, browser context, desktop app session, notebook kernel, MCP service, or helper server may belong to another AI agent running on the same machine, treat it as shared unless current-task ownership is proven.
15. Short-lived localhost validation services: when local HTML / app validation needs a safer fallback after `file://` is blocked, a task-owned loopback static server is allowed only within a bounded project or temp path, bound to localhost / loopback, and used for the current validation task. Record the served root, URL, and evidence collected. Stop the server before completion and verify it is no longer reachable when the runtime allows. Do not leave helper servers running as a convenience, expose them beyond loopback, reuse another agent's server without confirmation, or mutate browser profiles / extension state to make the validation pass.

## Checks

- Report which safety-relevant command, path, API, install, deploy, release, or Git check was performed and the result.
- If checks cannot run, state the reason and mark the result unverified.
- For durable governance changes, update the project index, sync registry, and any human review map if they exist.
- For external-tool resource cleanup, report the ownership class used: task-owned, agent-managed, shared / user-owned / other-agent-owned / system-level, or unknown.
- For short-lived localhost validation services, report the served root / URL, evidence collected, and cleanup result or cleanup blocker.

## Closeout

Record unresolved safety risks, blocked verification, pending manual actions, dirty worktrees, or external sync gaps in `dev/SESSION_HANDOFF.md`.
