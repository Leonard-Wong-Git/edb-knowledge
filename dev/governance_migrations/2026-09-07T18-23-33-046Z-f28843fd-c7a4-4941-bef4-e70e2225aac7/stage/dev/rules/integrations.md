# Integrations Pack

## Scope

Use this pack for governance of already-installed external tool integrations: **Connectors** (official or platform-vetted MCP servers), **MCPs** (community or custom MCP servers), **Plugins** (bundles that may register skills, MCP servers, hooks, or apps), and **Skills** (`SKILL.md` instruction sets).

When a task touches external sources or external write surfaces such as Notion, Google Drive, Dropbox, Slack, Linear, GitHub, HubSpot, browsers, screenshots, DevTools, Playwright, desktop app automation, crawlers, notebooks, or local helper services, this pack makes the agent check declared integrations and tool operation references first, prefer direct runtime access when available, and fall back to manual packets only when the integration is unavailable.

This pack does not teach users how to install tools. Installation is handled by the user's AI runtime, tool vendor, or official documentation. This pack governs what happens after a tool is already installed: declaration, verification, safe use, resource lifecycle, drift handling, and cross-session continuity.

## Load When

- The task mentions Notion, Google Drive, Slack, Linear, Dropbox, HubSpot, GitHub, browser automation, UI validation, screenshot capture, Chrome, Playwright, DevTools, desktop app automation, crawlers, notebooks, local helper services, or other external tools.
- The user asks whether the agent can directly read or write an external system.
- The current task or handoff names a declared integration as a dependency, or the user requests an integration health check.
- First-time onboarding asks the user to declare installed external tools.
- The project uses a multi-layer source-of-truth setup, for example Notion index + local source files + Google Drive reference mirrors.
- The user reports resource pressure, stale MCP or plugin services, browser automation left running, cache growth, or slowdown after external-tool use.

## Discipline

### 1. Credential Separation Principle

Credential values such as API keys, OAuth tokens, app secrets, and refresh tokens belong only in AI runtime secure storage, OS credential stores, tool configuration, environment indirection, or user-managed secret stores. Agent Handoff Kit files may record credential references, never credential values.

| Storage layer | Examples | What Kit files may record |
|---|---|---|
| AI runtime secure storage / Connector storage | Notion, Slack, Linear, Google Drive, Atlassian, HubSpot, or similar connectors | Storage type or connector name only |
| OS credential store | macOS Keychain, Windows Credential Manager, Linux secret service | `OS credential store` only |
| Tool config / env indirection | AI tool MCP config, plugin config, environment variable name | Config location or env var name only; never the value |
| User-managed secret store | Team vault or secret manager | Store type or owner only |

No file under `dev/` should contain a credential value. Enforce three rules:

1. Do not ask the user to paste credential values into chat.
2. If a credential-like prefix appears, redact it and warn the user to rotate the token when appropriate. Examples include `sk-`, `sk-ant-`, `ntn_`, `secret_`, `ya29.`, `1//`, `xoxp-`, `xoxb-`, `ghp_`, `gho_`, `ghs_`, `github_pat_`, `sl.`, `AKIA`, and `AIza`.
3. Before writing to `dev/PROJECT_INDEX.md` `## Installed Integrations`, self-check that no credential value is being persisted. Doctor also checks `PROJECT_INDEX`, `SESSION_HANDOFF`, and `SESSION_LOG` for common credential prefixes.

### 2. External Tool Usage Verification Gate

Agents must not use model memory, old session experience, copied examples, Connector marketing text, or guessed command shapes as the source for external-tool usage. Before first use of an external tool layer in the current task, and again before any write, destructive action, permission-sensitive action, raw API / SDK / CLI / URI call, plugin API change, or retry after `unknown tool`, `invalid arguments`, HTTP 400 / 404, permission, auth, or schema errors, verify the current usage source for that layer:

| Layer | Required current source before invocation |
|---|---|
| Connector / MCP tool | Current runtime-exposed tool name, description, and input schema. Use the tool list/schema exposed by the active AI runtime or MCP server; do not invent `mcp__*` names or arguments. |
| Plugin / Skill | Current plugin/skill instructions plus any registered MCP tool schema it exposes. |
| Raw API / SDK / CLI / URI | Current official documentation or a project-local runbook that states source, version/date, and scope. If the runbook lacks those, verify against official docs. |
| Local app plugin API | Official API documentation, official type definitions, official sample project, or local installed package types matching the project version. |
| Project-local runbook | Accept as a task source only when it records the upstream source, version/date, scope, and known limits. |

If the required source cannot be inspected, mark the tool use `blocked` or `unverified`, ask the user for the current docs/schema/runbook, or fall back to a manual packet. Do not continue by trial and error. Connector-first means schema-first for the active runtime, not memory-first.

#### Runtime-Controlled Tool Operation Variants

For browser and tool-operation work, first check `dev/PROJECT_INDEX.md` `## Tool Operation References` when present. A successful method from a previous session is reusable only when it is registered there with source, version/date, scope, known limits, and last verification.

| Variant | Examples | Required source before use |
|---|---|---|
| Browser / UI validation | Browser tool, screenshot, Chrome, DevTools, Playwright smoke test, visual QA | Active runtime browser/tool schema; registered tool operation reference; or current official docs for raw CLI/SDK use. Do not guess Chrome, Playwright, or DevTools commands. |
| Desktop or local app automation | Desktop app session, app plugin, local browser profile, extension-dependent workflow | Active app/plugin/tool schema or official automation API docs. Do not mutate user sessions, profiles, or extension state without confirmation. |
| Crawler / scraper / local helper | Firecrawl-like tools, crawler services, local helper server | Active tool schema, registered operation reference, or official docs. Respect source permissions, rate limits, and cleanup boundaries. |
| Notebook / data runtime | Notebook kernel, data runtime, long-lived analysis server | Active runtime/kernel schema or registered operation reference. Classify kernels and servers by ownership before cleanup. |
| Raw CLI / SDK / tool server | Direct command invocation, SDK script, MCP/tool server operation | Current official docs, installed package types, or registered operation reference. Mark blocked or unverified if unavailable. |

#### Local HTML / app validation fallback

A blocked browser surface is not the same as a blocked validation task. If a browser tool rejects a local `file://` page because of URL policy, sandbox policy, or browser-use safety policy, do not try to bypass that policy through raw CDP, alternate browser surfaces, extension state, or hidden browser commands. Treat the rejected `file://` attempt as one failed surface and switch to a materially safer project-local validation path when available.

For local HTML, static app, generated guide, or local UI validation, the preferred fallback is a short-lived localhost service:

1. Check `PROJECT_INDEX` `## Tool Operation References` for a registered browser, Chrome DevTools, Playwright, or local validation procedure.
2. If no registered procedure is available and the file can be safely served, start a task-owned local static server bound to loopback such as `127.0.0.1`.
3. Open the served `http://127.0.0.1:<port>/...` URL with the verified browser, DevTools, or Playwright surface.
4. Verify real behavior through visible page state, text hits, click/state changes, console evidence, screenshot, or another task-relevant readback.
5. Close the task-owned browser tab/context and stop the localhost service before completion; record any cleanup limit under the resource lifecycle rules.

Only mark local HTML / app validation as `blocked` after the registered operation reference, the localhost fallback, and the available verified browser / DevTools / Playwright surface are each unavailable or fail for a stated reason. A `file://` rejection alone is not enough evidence to stop.

### 2.1 External Tool Resource Lifecycle

External tools must be treated as resources with ownership, not just capabilities. After using Connector, MCP, plugin, browser automation, local server, crawler, notebook, or similar external tool services, classify any opened session, process, browser context, temporary directory, cache, or helper service into one of these ownership classes:

| Ownership class | Examples | Agent action |
|---|---|---|
| Task-owned | Process, browser context, temp directory, or helper service clearly started by this task and no longer needed. Evidence may include parent-child process chain, start time, tool family, task-created path, or runtime session handle. | Close or clean up automatically through the runtime or tool's graceful shutdown API when available; OS-level termination is allowed only when ownership is clear and graceful close is unavailable or failed. |
| Agent-managed | Kit-managed or agent-created temp/cache under a known task workspace, with bounded path and age/size rules. | Clean automatically inside the declared boundary. Never scan or clean broad user, system, browser, package-manager, or marketplace caches through this class. |
| Shared / user-owned / other-agent-owned / system-level | User's normal browser, another AI agent's active browser or MCP service, global MCP service, global npm/cache directory, shared credential store, project files, OS temp root, or any process whose owner is uncertain. | Do not terminate, delete, disable, or reconfigure automatically. Report evidence and propose exact remediation for user confirmation. |
| Unknown | Generic `node`, `python`, `chrome`, or helper process without reliable owner evidence. | Treat as shared until proven otherwise. |

For ordinary external-tool tasks, perform a lightweight closeout check: close task-owned handles, note any known retained session, and report only meaningful residual risk. For long-running, multi-tool, MCP-heavy, browser-automation, repeated-error, or user-reported slowdown tasks, perform a fuller resource review when the runtime exposes enough data: group by tool family, count, approximate memory where available, age / start time where available, and ownership class. If process command lines or environment details may contain secrets, redact arguments and secret-like values before reporting.

The preferred cleanup order is: graceful tool/session close, then task-owned process termination, then task-owned temp cleanup. Shared or ambiguous resources require explicit user confirmation with exact process IDs or paths, tool names, expected impact, and restart path before any termination, cache deletion, tool disablement, or configuration change. Never terminate or clean up a tool resource that may belong to another AI agent running on the same machine unless ownership has been proven for the current task.

### 3. Integration Type Discipline

#### 3.1 Connectors

Connectors are ready-to-use external tool surfaces exposed by the active AI runtime. Their credentials are normally managed by runtime secure storage, OS credential storage, or connector storage.

Discipline:

- Use only runtime-exposed tools whose current name, description, and input schema have been inspected.
- Read back every external write before claiming success.
- If auth fails, surface the failure and point the user to the runtime or connector settings. Do not attempt automatic re-auth.

#### 3.2 MCPs

MCP servers may be official, community, custom, or project-local. Custom MCPs often depend on manual configuration.

Discipline:

- Use only the active runtime's exposed tool name, description, and input schema.
- Treat non-vetted or custom MCP write operations with extra caution. Destructive writes require dry-run and user confirmation under `packs/safety.md`.
- If the server fails because of process crash, config error, or unavailable runtime state, surface the failure, recommend checking MCP config and restarting the host tool, and do not blindly retry.

#### 3.3 Plugins

Plugins are distribution bundles. A plugin may register skills, MCP servers, hooks, apps, or other runtime capabilities.

Discipline:

- Do not invoke a plugin as a separate abstraction unless the runtime exposes such an action.
- If a plugin provides a skill, follow the skill trigger rules.
- If a plugin provides an MCP server or app tool, treat it under the Connector / MCP rules above and the resource lifecycle rules in this pack.

#### 3.4 Skills

Skills are instruction overlays, usually stored as `SKILL.md`, and may be installed directly or shipped by a plugin.

Discipline:

- Invoke a skill when the user explicitly names it or when the skill's trigger conditions are clearly met.
- Skill instructions coexist with rule-pack discipline.
- If a skill conflicts with safety, governance, or closeout rules, the rule pack and core safety boundary take precedence.

### 4. Source-of-truth Architecture

When a project uses multiple integrations as a source-of-truth system, read `dev/PROJECT_INDEX.md` `## Installed Integrations` `### Source-of-truth Architecture` before acting.

| Layer | Role | Write direction |
|---|---|---|
| Source of truth | Original auditable reference content | User places or controls it; agent does not directly write it unless the project explicitly declares that integration as writable truth. |
| Index | Metadata, summary, tags, and references for source files | Agent may read/write through declared Connector or MCP when verified. |
| Persistent mirror | Backup or cross-device reference mirror | User-controlled sync by default; agent does not push automatically. |
| Working draft | Task output and local work product | Agent may read/write local files under normal safety rules. |

Each layer's responsible integration must be explicit in `PROJECT_INDEX`. Do not cross layers, for example by treating an index as primary truth or pushing a working draft to a mirror without authorization.

### 5. Cross-session Lifecycle

#### Phase 0 — First-contact declaration

During first-time onboarding, ask the user whether relevant external tools are already installed or available. This may be handled by the onboarding pack's external-tool scenario.

#### Phase 1 — Initial recording

Record declared integrations in `PROJECT_INDEX` `## Installed Integrations`, using the Connectors / MCPs / Plugins / Skills subsections and the Source-of-truth Architecture table when needed.

#### Phase 2 — Cross-session handoff

`SESSION_HANDOFF` durable anchors should point future agents to `PROJECT_INDEX` `## Installed Integrations`. The next-session opening message already includes `PROJECT_INDEX` in the read order.

#### Phase 3 — Before-use availability probe

Immediately before the current task uses a declared integration, run the smallest relevant availability probe when the runtime exposes the needed tool schema. Do not probe unrelated integrations at startup. `TBD`, examples, blank rows, and placeholder-only tables are not declarations.

- Probe success: update `Last Verified` and proceed.
- Probe fail: warn that the integration is declared but unavailable in the current runtime, then use fallback flow only for the affected surface.

#### Phase 4 — Task execution

Apply the knowledge pack's Connector-first discipline: check declaration, use the verified direct tool when available, fall back to manual packet only when unavailable, and ask the user when the referenced integration is undeclared.

#### Phase 5 — Mid-session drift handling

If an integration fails mid-task because of expired auth, rate limit, network timeout, tool crash, or missing runtime capability:

- Surface the failure and impact.
- Do not auto-fix credentials or auth.
- Update `PROJECT_INDEX` `Last Verified` / note fields where appropriate.
- Record the drift in `SESSION_LOG` and unresolved risk in `SESSION_HANDOFF` when it affects future work.

#### Phase 6 — Cross-tool consistency

Integration declarations are project-level; they do not guarantee every AI runtime has the same tools installed. A new runtime must verify availability, warn on capability differences, and use fallback flow unless the user chooses to install or switch tools.

## Rules

1. **Credential separation**: never ask for, log, or persist credential values. Redact credential-like values and warn about rotation when appropriate.
2. **External Tool Usage Verification Gate**: verify current runtime schema, official docs, official types/samples, or registered tool operation references before invoking or retrying external tools.
3. **Declaration before use**: read `dev/PROJECT_INDEX.md` `## Installed Integrations` and `## Tool Operation References` before external-tool or runtime-controlled tool-operation work. If absent, ask about integration status rather than assuming none exists.
4. **Connector-first default**: when a declared integration is functional, prefer the verified direct tool call. Manual paste is fallback, not default.
5. **Write operations require read-back verification**: read back every external write before claiming success.
6. **No auto-fix credential / auth issues**: surface auth failures to the user and point to the runtime settings or tool owner.
7. **Cross-tool capability awareness**: verify availability immediately before use, when the current objective declares the integration as a dependency, or when the user requests a health check.
8. **Do not cross source-of-truth layers**: follow the role and write direction declared in `PROJECT_INDEX`.
9. **Drift event mandatory recording**: record integration drift in `PROJECT_INDEX`, `SESSION_LOG`, and `SESSION_HANDOFF` when it affects future work.
10. **Plugin / Skill subordination**: plugin and skill instructions coexist with rule packs; safety, governance, and closeout rules take precedence on conflict.
11. **External tool resource lifecycle**: after external-tool use, classify resources by ownership. Task-owned / agent-managed resources may be closed or cleaned automatically; shared, user-owned, system-level, other-agent-owned, or unknown resources require evidence reporting and user confirmation before remediation.
12. **Local HTML / app validation fallback**: if `file://` browser access is blocked, do not bypass the policy and do not stop on that single surface failure. Use a registered operation reference or a short-lived loopback localhost service for actual browser / DevTools / Playwright validation, then close the task-owned service and record the evidence.
13. **Terminal-state contract**: a tool operation succeeds only when the runtime returns an explicit successful terminal state and any required read-back passes. Stopped, aborted, timeout, spawn / transport error, signal, missing final result, or partial stdout before termination makes the affected operation indeterminate or failed, not successful. It does not make unrelated already-verified task evidence permanently invalid. For read-only operations, verify the state and rerun only the affected operation when still needed. For any operation that may have written externally or to disk, read back the actual target state before retrying, recovery, or success claims.

## Checks

- Verify `dev/PROJECT_INDEX.md` `## Installed Integrations` exists and has the expected subsections when the project declares integrations.
- Before probing or invoking a declared integration, inspect current runtime tool description and input schema.
- Before browser validation, screenshots, Chrome, Playwright, DevTools, desktop automation, crawler, notebook, or raw CLI/SDK/tool-server work, verify the current source from runtime schema, official docs, or `PROJECT_INDEX` `## Tool Operation References`.
- Before external-tool first use, write, destructive operation, raw API / SDK / CLI / URI / plugin API call, or retry after tool error, confirm the current usage source.
- Surface and record mid-session integration drift.
- After external-tool use, perform ownership-based resource closeout. For long-running, multi-tool, MCP, browser automation, repeated-error, or slowdown scenarios, report grouped residual processes or services when observable.
- Before closeout, update `Last Verified` for integrations touched this session.
- Self-check credential leakage before writing `PROJECT_INDEX`, `SESSION_HANDOFF`, or `SESSION_LOG`.
- Verify that `PROJECT_INDEX` External Sources `via` references match declared Installed Integrations entries.
- For local HTML / app validation, verify that a rejected `file://` attempt is followed by a registered operation reference or short-lived localhost fallback before declaring `blocked`.
- Treat stopped, aborted, timeout, spawn / transport error, signal, and missing final result as operation-level indeterminate / failed states. Never count partial stdout, a wrapper exit code, or an outer command's success as terminal success without the expected final state and read-back.

## Closeout

1. Update `PROJECT_INDEX` `## Installed Integrations` `Last Verified` cells for integrations touched this session.
2. If drift happened, record the drift narrative, impact, and suggested next handling in `SESSION_LOG`.
3. Add unresolved integration failures to `SESSION_HANDOFF` `## Risks / Blockers`.
4. If unresolved drift affects startup, mention the next-session verification need in the opening message.
5. If the user declared a new integration during the session, ensure it is registered in `PROJECT_INDEX` and cross-referenced from External Sources when applicable.
6. If shared or ambiguous external-tool processes, caches, browser contexts, or helper services remain, record only a redacted evidence summary and recommended remediation. Do not write raw secret-bearing command lines into handoff or log files.

## Anti-patterns

| Anti-pattern | Why it is wrong | Correct approach |
|---|---|---|
| Assuming no Connector or MCP exists whenever the user mentions Notion, Google Drive, or another external source | Mature connector ecosystems make paste-only fallback an unreliable default. | Read `PROJECT_INDEX` Installed Integrations first; ask about integration status if undeclared. |
| Guessing tool names, endpoints, CLI flags, URI parameters, or plugin APIs from memory | Stale examples cause unknown tool, invalid args, 400 / 404, permission, or auth loops. | Verify active runtime schema, official docs, official types/samples, or versioned local runbooks. |
| Treating browser validation as ordinary coding and guessing Chrome, Playwright, or DevTools commands | Browser and tool-control surfaces differ across runtimes, profiles, plugins, and installed packages. | Verify the active runtime schema, official docs, or a registered tool operation reference; mark blocked or use a manual packet when unavailable. |
| Treating a Connector marketing page or old example as executable schema | Marketing pages do not prove the active runtime's current tool name or input schema. | Use active runtime tool list/schema as the invocation source. |
| Retrying unknown tool / invalid args by changing names or parameters repeatedly | Trial-and-error hides the real schema or docs gap. | Stop same-pattern retries and return to the External Tool Usage Verification Gate. |
| Writing credential values into `PROJECT_INDEX`, `SESSION_HANDOFF`, or `SESSION_LOG` | Project files and git history are persistent; leaked credentials remain exposed. | Record credential references only, never values. |
| Using a credential value pasted in chat and then recording it | Chat history and logs may persist the secret. | Redact, warn, and ask the user to rotate if needed. |
| Auto-fixing auth or re-auth flows | Auth belongs to the user and the runtime/tool boundary. | Surface the failure and point to the runtime or tool settings. |
| Claiming an external write succeeded without read-back | External writes may fail silently or partially. | Read back and compare before claiming success. |
| Crossing source-of-truth layers | It can corrupt truth, mirrors, or working drafts. | Follow the declared layer role and write direction in `PROJECT_INDEX`. |
| Skipping current availability verification because an old handoff said the tool worked | Tokens expire, runtimes change, and tools can be removed. | Probe availability in the current runtime before using the integration. |
| Treating stopped, aborted, timeout, spawn / transport error, signal, missing final result, or partial PASS output as success | Tool output can be partial, wrappers can hide inner failure, and external writes may be unknown. | Mark the affected operation indeterminate or failed; read back any possible write target before retrying or claiming success. |
| Leaving task-owned MCP / browser / helper processes running after the task | Turns one-off tool use into a long-lived resource leak and can slow the host. | Use graceful close or task-owned process cleanup automatically; switch to user confirmation only when ownership is unclear. |
| Broadly killing by process name such as `node.exe`, `python`, or `chrome` | A generic process name does not prove ownership and may terminate user work, another project, or another AI agent's active tools. | Classify by tool family, process ID, start time, parent chain, and task-created path; treat unknown ownership as shared. |
| Automatically cleaning global caches, marketplace caches, OS temp roots, or browser profiles | May remove shared state, login state, or data other tools still need. | Automatically clean only task-owned / agent-managed bounded paths; report evidence and wait for confirmation otherwise. |

## Cross-reference

- `packs/knowledge.md` Rule 5: Connector-first source access discipline.
- `packs/safety.md` Rule 10: external API / SDK / CLI / tool verification boundary.
- `packs/safety.md` Rule 12: credential leak prevention.
- `packs/safety.md` Rule 14: process termination and cache cleanup boundary for external-tool resources.
- `packs/onboarding.md` Scenario F: first-contact declaration entry point.
- `runtime-core/AGENTS.core.md` Section 1: task-triggered availability probe discipline.
- `runtime-core/PROJECT_INDEX.md` `## Installed Integrations` and `## External Sources` `via` column: declaration registry.
