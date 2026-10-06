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
   (b) If a declared Integration is functional in the current session (verified under the task-triggered availability probe in installed `AGENTS.md`): use only the active runtime tool calls whose current name, description, and input schema have been inspected under the External Tool Usage Verification Gate. Do not invent `mcp__*` names or arguments from examples or memory.
   (c) If a declared Integration is unavailable in the current session, follow `dev/rules/integrations.md` fallback: classify the actual failure, check a task-authorized capable channel and normal platform approval, and use a manual packet only when it preserves the needed evidence. Record drift honestly; update `Last Verified` only after a real successful probe and the normal Persistence Gate.
   (d) If no declaration exists in `## Installed Integrations` but the task references an external tool: first inspect the active runtime for an authorized capable tool/schema. Ask the user only for access, source information, or a decision that the AI cannot obtain; do not silently assume paste fallback. Backward-compat: existing v0.2.x projects with no Installed Integrations section follow the same bounded capability check before any necessary user question.
6. When writing to an external mirror or index, read back the written record before claiming sync success.
7. Preserve local file paths as plain text, code, or structured rich text fields when the external tool parses Markdown links or escape characters.

## Checks

- Verify external source identity, timestamp, and scope.
- Check `dev/DOC_SYNC_REGISTRY.md` for required sync targets and status vocabulary.
- Record conflicts between local and external content.
- Mark unread relevant sources as unread, pending, or blocked. Do not treat unread sources as absent.

## Closeout

Record external sync status, pending paste/manual steps, unresolved conflicts, and next verification point.
