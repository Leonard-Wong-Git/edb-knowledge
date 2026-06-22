# Communication Pack

## Scope

Use for reply format, language behavior, output schema, user-facing explanation, and cross-agent handoff wording.

## Load When

- User requests a specific response format, language, style, report, review, or schema.
- The task changes public-facing instructions or AI-facing reply discipline.

## Rules

1. Match the user's language unless a project file requires another language.
2. Lead with decisions, findings, or results before background.
3. Mark assumptions and unverified facts.
4. Keep operational instructions copy-paste-ready when they are meant for future sessions.
5. Avoid exposing internal process unless it helps the user act.

## Checks

- Verify required headings, schema fields, or language split.
- Check public README or docs if user-facing behavior changed.
- Confirm handoff/opening messages are complete and root-specific when needed.

## Closeout

Record any durable response-format decisions and where they were persisted.
