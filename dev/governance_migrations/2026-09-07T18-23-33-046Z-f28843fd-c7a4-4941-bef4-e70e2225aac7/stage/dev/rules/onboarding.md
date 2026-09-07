# Onboarding Pack

## Scope

Use this transient pack for first-time Agent Handoff Kit users after a fresh install, users who request guidance, or when the user's first-task intent remains genuinely unresolved after reading the available project state.

The goal is to help the user complete a small first task without requiring them to read README, guide pages, `AGENTS.md`, or internal Kit rules first. After the onboarding walk-through finishes, unload this pack and continue with the regular scenario pack such as coding, research, writing, knowledge, or integrations.

## Load When

### Explicit onboarding signal keywords

Load this pack when the user message contains an onboarding signal such as:

- "I'm new" / "new user"
- "teach me" / "help me start" / "help me get started"
- "first time" / "first-time" when the user also asks for guidance
- "how do I start" / "show me how" / "getting started"
- "what can agent handoff kit do"
- vague project intent such as "I want to do a project"
- equivalent Chinese user phrases such as "新手", "教我用", "點開始", "能力", or "能做甚麼"

`I just installed` / "我剛安裝" is a first-use signal. When `SESSION_HANDOFF` says `First-use guidance state: eligible` and no executable objective remains, load this pack and give the first-use welcome. It does not override a same-message concrete task with enough material facts.

### Continuity startup boundary

`Start Agent Handoff` / "開工" starts continuity and reads the minimum current handoff state; it is not an onboarding signal by itself. A plain startup normally stops after its status card and recommended next action; a loaded objective alone does not authorize work. First-use eligible plain startup is the exception: when the handoff says `First-use guidance state: eligible`, the active objective is empty / `TBD`, and the user did not provide a same-message concrete task, enter onboarding instead of ending status-only. A same-message concrete task may begin normally. Only when no executable objective remains after state reading should the AI ask one concise question or offer the guided onboarding path. Explicit requests such as "新手，教我用" enter onboarding directly.

### Implicit signals

- The first user message is short and still genuinely vague after available project state is read.
- `SESSION_HANDOFF` first-use guidance state is `eligible`, Active Objective is empty / `TBD`, and the user has not supplied a concrete objective with enough material facts. This is the fresh-install welcome path and should not be skipped as an ordinary status-only startup.
- The user asks a generic capability question instead of giving a concrete task.
- The user appears unfamiliar with the workflow, for example asking what the AI should do rather than giving an objective.

## Discipline

### 1. Do not assume prior reading

The user may start directly from an AI conversation. Explain only the minimum needed for the current step. Do not teach internal file structure, pack names, release identifiers, maintenance rules, or implementation details unless the user asks.

### 1.1 Public capability answer

When the user asks "教我用", "能力", "能做甚麼", "what can agent handoff kit do", or an equivalent broad help question, answer in normal user language first. The main answer is what the user can say to an AI, not a CLI command list.

Start broad help / capability answers with this display-only onboarding card in a fenced `text` block:

```text
   /\_/\   Agent Handoff Kit
  ( o.o )  quick guide
   > ^ <
```

The card is a brand affordance only. It must not claim `continuity ready`, `handoff saved`, a version, loaded state, doctor health, or that `SESSION_HANDOFF.md` has been read. Do not perform extra reads, `doctor`, version checks, or handoff loading merely to fill the card.

Cover these public command categories:

- Daily continuity: say "開工" / "Start Agent Handoff" to resume, and "收工" / "wrap up" to save a handoff.
- Keep important files connected: say "把這份文件接入 Agent Handoff Kit，讓下次 AI 知道何時要讀、何時要更新。" / "Connect this document to Agent Handoff Kit so the next AI knows when to read and update it."
- Find missing governance links: say "掃描未接入 Agent Handoff Kit 的重要文件。" / "Scan for important documents not yet connected to Agent Handoff Kit."
- Turn a recurring mistake into future practice: say "把今次錯誤整理成日後工作規則，讓下次 AI 知道要怎樣避免。" / "Turn this mistake into a durable work rule for future sessions."
- Keep an API / MCP / tool-use practice reusable: say "以後都用這個 API 調用方式，之後開新對話也要沿用。" / "Use this API approach in future sessions too."
- Declare external tools safely: say "這個項目會用到這些外部工具，請記住哪些能直接使用，機密不要寫入項目文件。" / "Record what external tools can be used directly and keep secrets out of project files."
- Finish a long external-tool task cleanly: say "收工時請顯示外部工具資源收口結果：已關閉哪些本任務資源，哪些因歸屬不明而保留並列證據。" / "At wrap up, show the external-tool resource closeout."

Do not make CLI maintenance commands the main onboarding answer. Mention `init`, `upgrade`, `doctor`, `workspace-health`, or `closeout-status` only when the user asks about installation, upgrade, repair, health checks, manual terminal use, or when the current task needs those checks. For a zero-background user, phrase maintenance as "the AI can install, upgrade, or check the Kit when needed" before exposing exact commands.

### 2. Infer first; offer scenario choice only when needed

Infer when sufficient; ask only when unresolved. Read the user's message together with the available handoff and project state before deciding whether a chooser is needed.

When the user has already supplied a concrete, actionable objective and enough material facts, infer the closest working scenario, state the assumption briefly, load the regular task pack(s), and begin the first safe action. Do not require an A-F reply, repeat questions whose answers are already available, or reduce a concrete request to a generic minimum task.

Only show the scenario chooser when the user's intent remains genuinely unresolved or the user asks for guided onboarding. In that case, combine the startup card and chooser into one complete response. Do not print a partial startup card first or repeat the card.

This routing decision never removes a safety gate. High-risk, external, permission, cost, publishing, and irreversible actions still require the normal plan and explicit confirmation before execution.

The library contains six scenarios. Treat them as an internal inference library. When choices are genuinely required, show only the two or three most relevant options; use a short open question when no responsible shortlist can be inferred. Do not display all six merely because the library contains them.

- **A. Build systems, tools, platforms, websites, or apps**: the user wants AI help to create or maintain a working project.
- **B. Organize research or write a report**: the user has sources, notes, articles, presentations, or a report goal.
- **C. Organize local files, Notion, Google Drive, or a knowledge base**: the user wants source, reference, mirror, and draft material kept clear.
- **D. Learn to code**: the user is a technical beginner and wants a small guided exercise.
- **E. Custom scenario**: the user has another goal.
- **F. Review installed external tools and design governance**: the user already has Connectors, MCPs, Plugins, Skills, or browser / notebook / crawler tools and wants a safe operating model.

### 3. Guided 5-step walk-through pattern

Use this five-step path only after the user selects guided onboarding or when clarification is genuinely needed:

1. Confirm project context: folder, existing material, current tools, source locations, and whether external tools are already connected.
2. Explain in three plain points how Agent Handoff Kit helps this scenario.
3. Ask for the first concrete task scope, offering at most two or three genuinely relevant options.
4. Suggest one minimum viable task that can usually be completed in 10-15 minutes.
5. Wait for user confirmation, then transition to the regular work loop.

### 4. Ask only for missing information

Skip any guided step already answered by the user or available project state. When a step is still needed, advance one step at a time and:

- state what the AI will do,
- state what the user needs to answer or confirm,
- answer questions before continuing,
- let the user skip or change the step.

### 5. Keep the first task small

The first task should be a preview, a short draft, a small classification sample, a dry-run, or another bounded result. Do not begin with broad refactors, bulk file moves, publishing, deployment, or destructive operations.

### 6. Transition after onboarding

After the walk-through:

- load the regular pack(s) for the chosen task,
- unload this transient onboarding pack,
- enter the PLAN -> READ -> CHANGE -> QC -> PERSIST work loop,
- record the first-task scope in `SESSION_HANDOFF` when the persistence gate requires it.

## Application Scenario Library

Each scenario is a fallback guidance template, not a mandatory questionnaire. The model may skip answered steps, infer the route when evidence is sufficient, and adapt wording while preserving intent, tone, and safety boundaries.

### Scenario A. Build systems, tools, platforms, websites, or apps

Step A.1: ask for the project folder, current stack if known, whether git exists, and whether GitHub, Linear, Slack, Notion, Google Drive, or other external tools are connected.

Step A.2: explain that Kit helps the AI remember project state across sessions, avoid silent risky commands, and record what changed at closeout.

Step A.3: offer task choices such as fix a bug, add a feature, organize code, add tests, write README, or prepare a first commit.

Step A.4: suggest a small first task, such as a short README section, one failing test investigation, or a dry-run plan.

Step A.5: after confirmation, load the relevant coding / writing / safety packs and begin the normal work loop.

### Scenario B. Organize research or write a report

Step B.1: ask for the topic, existing source locations, intended reader, and whether Notion, Google Drive, or another source tool is connected.

Step B.2: explain that Kit separates source evidence from inference, records source locations, and preserves progress across sessions.

Step B.3: offer task choices such as outline sections, register sources, summarize one source, draft a subsection, or review an existing draft.

Step B.4: suggest a small first task, such as a 5-7 heading outline with one sentence per section.

Step B.5: after confirmation, load research / writing / knowledge packs and begin the normal work loop.

### Scenario C. Organize local files, Notion, Google Drive, or a knowledge base

Step C.1: ask what needs organizing: local folder, Notion database, Google Drive folder, or mixed sources. Ask which external tools are connected or unknown.

Step C.2: explain that Kit separates source of truth, references, mirrors, and drafts, and that risky file operations require dry-run and confirmation.

Step C.3: offer task choices such as scan and classify files, design a folder structure, draft a Notion schema, write a dry-run script, or align local references with an external index.

Step C.4: suggest a small first task, such as classifying a bounded sample without moving files.

Step C.5: after confirmation, load knowledge / safety / integrations packs as needed.

### Scenario D. Learn to code

Step D.1: ask which direction the user wants: small automation, web page, Python tool, Git / GitHub basics, or another beginner task. Ask whether any relevant tools are already installed.

Step D.2: explain that Kit keeps learning progress across sessions, keeps risky operations explicit, and lets the user review each small change.

Step D.3: offer one small exercise, such as a dry-run file renamer, a one-page HTML example, or a tiny Python script.

Step D.4: keep the exercise small enough to explain line by line.

Step D.5: after confirmation, load coding / safety packs and begin the normal work loop.

### Scenario E. Custom scenario

Step E.1: use any facts already provided, then ask only for missing information that materially affects the first safe action. Do not ask about technical comfort unless it changes the delivery approach.

Step E.2: explain how Kit helps the chosen scenario using continuity, safety, and source / artifact governance.

Step E.3: offer task choices tailored to the user's answer.

Step E.4: suggest one minimum viable first task.

Step E.5: after confirmation, load the appropriate regular pack combination.

### Scenario F. External-tool governance

Use this scenario when the user already has external tools installed or asks how to use them safely across sessions. This scenario does not teach installation. It records declarations, boundaries, verification, and safe use.

Step F.1: collect installed external tools by category: Connectors, MCPs, Plugins, Skills, browser automation, crawlers, notebooks, or local helper services. If the user does not know the category, ask for names only and classify them.

Step F.2: explain credential separation: Kit files record tool names, project usage, access scope, and credential reference location only. They must never store API keys, OAuth tokens, secrets, or credential values.

Step F.3: map source-of-truth architecture: source of truth, index, persistent mirror, and working draft. Make each layer's write boundary explicit.

Step F.4: when authorized, write the declaration into `PROJECT_INDEX` `## Installed Integrations` and cross-reference relevant External Sources `via` values.

Step F.5: verify current availability using runtime-exposed tool schemas, official docs, or versioned local runbooks. Mark unavailable tools as blocked / unverified instead of guessing.

## Cross-reference to guide.html

When the user asks for a fuller example, mention `agent-handoff-kit-guide.html` as an optional reference. The guide is not required reading.

- Case A aligns with Scenario A plus parts of Scenario C.
- Case B aligns with Scenario B plus Scenario F.
- Case C aligns with long-running project evolution.

## Tone Discipline

Use plain user-facing language. Avoid internal jargon in onboarding replies unless the user asks for implementation details.

- Say "project registry" before exposing `PROJECT_INDEX`.
- Say "wrap up" or the user's own closeout phrase before exposing closeout internals.
- Say "next-session startup message" only when discussing the persisted handoff file.
- Say "working mode" before exposing "rule pack".
- Say "risky command" before exposing "destructive operation".

Keep user-facing explanations self-contained. For the public product's Chinese surfaces, use steady written Traditional Chinese and avoid Cantonese spoken characters. Inside this AI-facing pack, keep instructions in English and use Chinese only as quoted user phrases that the runtime must recognize.

## Closeout

After onboarding finishes:

1. Confirm that the user knows the next practical action, how to start a later session, and how to request closeout.
2. Update `SESSION_HANDOFF` only when the persistence gate says the first-task scope or next action is durable.
3. Record next priorities only when they affect a later session.
4. Do not paste a separate stateful opening message in chat. The persisted `SESSION_HANDOFF` opening-message block remains authoritative.
5. Unload this pack and continue with the relevant regular pack(s).
6. Mark `ack:field:first-use-guidance-state` as `consumed` after the first guided task begins or the first full closeout completes. Never reset `consumed` or `not_applicable` to `eligible` during upgrade.

In a later session, reload onboarding only when the user gives a fresh onboarding signal or asks to restart the walk-through. Otherwise enter the normal work loop.

## Anti-patterns

| Anti-pattern | Why it is wrong | Correct approach |
|---|---|---|
| Treating a genuinely vague first message as a specific task | The user may be trying to learn the workflow or choose a scenario. | Ask one concise question or show the two or three most relevant scenarios only when intent remains unresolved. |
| Making the first task broad | A first-time user needs rhythm and confidence before large changes. | Suggest one 10-15 minute minimum viable task. |
| Explaining Kit internals before the user needs them | Internal labels increase cognitive load. | Explain the visible effect in plain language. |
| Assuming the user read README or guide pages | Many users start directly in an AI chat. | Surface only the concepts needed for the next step. |
| Keeping onboarding loaded after the first task starts | Onboarding is transient and will distract from normal task work. | Unload onboarding and load the regular pack(s). |
| Forcing the chooser or all five guided steps after the objective is already concrete | The user must repeat known information and the AI shifts technical work back to the user. | Infer the scenario, state the assumption, and begin the first safe action; ask only for missing facts or required risk approval. |
| Assuming no Connector, MCP, Plugin, or Skill exists | Paste-only fallback creates the wrong operating model for users who already connected tools. | Ask a lightweight external-tool question in step 1, or use Scenario F. |
