# Rule Packs Router

Read only the packs needed for the current task.

| Task signal | Pack | Purpose |
|---|---|---|
| First-time user signals (任一即可): "I'm new" / "新手" / "教我用" / "help me start" / "first time" / "我啱啱安裝" / "點開始" / "show me how" / "getting started" / "agent handoff kit 可幫我做甚麼" / "我想做 [type] project" / "點用" / "能力" / vague first message ≤ 30 chars / HANDOFF Active Objective 空白 + Session count 1 (fresh installation context) | `dev/rules/onboarding.md` | first-time user walk-through with 6 scenarios (A 建構系統 / B 研究報告 / C 知識庫 / D 學寫代碼 / E 其他 / F 外部工具治理) × 5-step pattern (PLAN-style: confirm context / explain v2 fit / ask task scope / suggest minimum viable / confirm + transition); load proactively when signal present; transient pack, unload after onboarding completion |
| Destructive file operations, shell writes, Git state changes, package managers, installers, deploy, release, cloud tools, external APIs, credentials, locked files, permission errors | `dev/rules/safety.md` | safety checks for data loss, external systems, secrets, and high-risk operations |
| Code, tests, build, package manager, SDK, CLI, API | `dev/rules/coding.md` | development workflow and verification |
| Draft, edit, style, publication content | `dev/rules/writing.md` | writing workflow and tone control |
| Sources, evidence, comparison, fact finding | `dev/rules/research.md` | source handling and uncertainty |
| Governance, prompts, agents, handoff, startup/closeout, skills | `dev/rules/agent-governance.md` | governance changes and boundary control |
| Governance bridge / 治理打通 / 把文件接入 Agent Handoff Kit / 接入 Agent Handoff Kit / 掃描未接入 Agent Handoff Kit 的重要文件 / bridge governance / connect this document to governance / scan for unbridged governance documents | `dev/rules/agent-governance.md` | connect important files, source-of-truth documents, runbooks, workflows, checklists, and guides to the project index, sync registry, handoff/log roles, and related workflows without creating duplicate sources of truth |
| Long-term governance routing / 寫入長期治理 / 轉成長期機制 / 之後都要遵守 / 跨 session 有效 / future sessions should remember / always use this API or MCP pattern | `dev/rules/agent-governance.md` | classify durable non-file knowledge by role and store it in the right home: rule pack, registered reference, project index, sync registry, project decisions, or QA check; do not leave reusable governance only in session log or handoff |
| Release, publish, deploy, tag, hotfix, GA | `dev/rules/release.md` | release verification and evidence |
| External notes, knowledge base, Notion, Obsidian, Google Drive | `dev/rules/knowledge.md` | external knowledge source integration |
| External tool integrations (Connector / MCP / Plugin / Skill) — declared in `## Installed Integrations`; tasks involving Notion / Google Drive / Slack / Linear / Dropbox / HubSpot / GitHub / etc. external read-write | `dev/rules/integrations.md` | Connector-first default + credential separation + multi-layer source-of-truth + cross-session resilience |
| Reply format, language, output schema — **plus any task whose reply will state a measurement, a count, a pass/fail rate, a root cause, or an account of what the agent did or did not do** (S196: claim discipline must load when the claims are made, not only when wording is the topic) | `dev/rules/communication.md` | user-facing response rules + claim discipline (evidence required before a verdict; direction-of-error trigger) |

## Routing Rule

Load the minimum set. If uncertain, load the narrower pack first. If a task clearly involves safety risk plus another domain, load `dev/rules/safety.md` with the relevant domain pack and state why. Packs can add stricter rules, but cannot weaken core safety or closeout requirements.
