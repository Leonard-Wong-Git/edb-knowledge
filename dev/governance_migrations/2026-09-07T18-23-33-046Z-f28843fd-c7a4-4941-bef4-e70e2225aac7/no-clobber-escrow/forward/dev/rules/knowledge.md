# Knowledge Pack

## Scope

Use for external notes, knowledge bases, Notion, Obsidian, Drive, docs repositories, and source-of-truth mapping.

## Load When

- User references external knowledge tools or asks to sync project knowledge outside local files.
- Project truth may be split between local markdown and an external system.

## Rules

1. Determine whether the external surface is source of truth, mirror, index, or attachment store.
2. Record access mode and sync expectation before relying on external content.
3. Prefer local durable files for installable runtime text unless the project declares otherwise.
4. Do not perform destructive external writes without explicit confirmation.
5. Connector-first default for external read/write (R-030 Integration governance discipline; works together with `dev/rules/integrations.md`):
   (a) Before reading or writing external knowledge, check `dev/PROJECT_INDEX.md` `## Installed Integrations` for declared tool availability.
   (b) If a declared Integration is functional in the current session (verified during startup probe per `runtime-core/AGENTS.core.md` Section 1): use the corresponding `mcp__<tool>__*` tool calls directly (e.g. `mcp__notion__fetch` / `mcp__notion__create-pages` / `mcp__google-drive__list`).
   (c) If a declared Integration is unavailable in the current session (different AI tool / Connector not configured / auth expired): degrade to manual paste packet workflow + flag drift in the mid-task summary + update `Last Verified` cell at closeout.
   (d) If no declaration exists in `## Installed Integrations` but the task references an external tool: ask the user about Integration status before proceeding (do not silently assume paste fallback). Backward-compat: existing v0.2.x projects with no Installed Integrations section follow path (d) — the section template auto-appends on upgrade but content stays empty until user declares; AI behavior degrades gracefully to ask-user fallback.
6. When writing to an external mirror or index, read back the written record before claiming sync success.
7. Preserve local file paths as plain text, code, or structured rich text fields when the external tool parses Markdown links or escape characters.

## Checks

- Verify external source identity, timestamp, and scope.
- Check `dev/DOC_SYNC_REGISTRY.md` for required sync targets and status vocabulary.
- Record conflicts between local and external content.
- Mark unread relevant sources as unread, pending, or blocked. Do not treat unread sources as absent.

## Closeout

Record external sync status, pending paste/manual steps, unresolved conflicts, and next verification point.
