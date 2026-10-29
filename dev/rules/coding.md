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

## Project Rules

### 定期系統更新檢查（S241，2026-10-29，Leonard 定案）

外部模型、依賴套件與執行環境會在本系統沒有改動的情況下過期（S237 才發現 OpenAI 停用舊模型、S240 才補依賴漏洞）。所以要定期主動檢查，不等出事。

1. **頻率**：每 30 日最少一次。以 `dev/PROJECT_INDEX.md` 指令表「定期系統更新檢查」一行的最後核實日期為準。單獨「開工」只在起手卡「注意事項」提示已逾期；要到 Leonard 授權任務的回合才執行。
2. **範圍**（逐項記結果；查不到的寫明原因，不可當作通過）：
   - 外部模型／API：重讀 `dev/CODEBASE_CONTEXT.md` External Services 列出的官方停用頁與價錢頁，核對生產合成、相關性判官、量度判官、OCR、embedding 所用型號有否公布停用或改價。
   - 依賴漏洞：`backend/` 與 `dev/checklists/_work/` 的 `npm audit`。
   - 執行環境：本機 Node、`/usr/local/bin/python3`（openai、fitz）及 Render 執行環境有否到期或停止支援。
   - 自動監察：`.github/workflows/` 各排程監察最近一次是否成功，有否未處理的 Issue。
   - Agent Handoff Kit：是否有新版本。
3. **結果**：更新該行的最後核實日期與摘要；需要處理的事項寫入 `dev/SESSION_HANDOFF.md` `Open Priorities`。檢查本身只讀；修補、付費 API 呼叫、合併或部署仍按原有規則逐項取得批准。
