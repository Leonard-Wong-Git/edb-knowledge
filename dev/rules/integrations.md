# Integrations Pack

## Scope

外部工具治理 pack —— 處理用戶已安裝嘅四類整合：**Connectors**（Anthropic 官方 vetted MCP server）、**MCPs**（community / custom MCP server）、**Plugins**（Claude Code plugin bundle）、**Skills**（SKILL.md instruction set）。

當任務涉及外部來源讀寫（Notion / Google Drive / Dropbox / Slack / Linear / GitHub / HubSpot 等），本 pack 引導 AI 先檢查項目已 declare 嘅整合，優先使用直接 access（Connector / MCP tool calls），fallback 至 paste packet 只當整合 unavailable 時。

本 pack **不教用戶 install** —— 安裝行為屬 intermediate 用戶責任，由 Anthropic 官方 / 各工具自身文檔負責。本 pack 只專注「**用戶已裝好之後，點樣治理跨 session 穩定可用**」。

## Load When

- 任務描述提到 Notion / Google Drive / Slack / Linear / Dropbox / HubSpot / GitHub / 其他外部工具
- 用戶問「我可以叫 AI 直接讀 / 寫 Notion / Google Drive / 等嗎？」
- 項目 `dev/PROJECT_INDEX.md` `## Installed Integrations` section 非空
- 第一次安裝後 onboarding 階段（與 `dev/rules/onboarding.md` 配合，新手 declare 已裝工具）
- 後續任務涉及多源 governance（譬如 Notion DB Index + 本機真源 + Google Drive 參考檔三層持久化組合）

## Discipline

### 1. 機密分離原則（最高優先）

**Credential（API key / OAuth token / app secret / refresh token）由 AI 工具自身 secure storage 管理**，與本 Kit 完全分離：

| 儲存層 | 例子 | 加密方式 |
|--------|------|----------|
| Claude Desktop Extensions（one-click install） | Notion / Slack / Linear / Google Drive / Atlassian 等 | OS Keychain (macOS) / Credential Manager (Windows) auto-encrypt |
| Claude Code MCP config | `~/.config/claude-code/mcp.json` 等（manual setup） | 用戶自管（env var / OS secure storage） |
| 其他 AI tool（Codex / Gemini CLI 等）自身 config | tool-specific 路徑 | tool-specific 加密 |

Kit 嘅 `dev/` folder **任何檔都不 touch credential value**。三條硬性 enforcement：

1. AI 不要求用戶喺對話貼 credential value
2. AI 識別到 credential prefix（`sk-` / `sk-ant-` / `ntn_` / `secret_` / `ya29.` / `1//` / `xoxp-` / `xoxb-` / `ghp_` / `gho_` / `ghs_` / `github_pat_` / `sl.` / `AKIA` / `AIza` 等）會即時 redact + warn 用戶 rotate token
3. 寫入 `dev/PROJECT_INDEX.md` `## Installed Integrations` 前 self-check 確認無 credential leak；doctor `checkInstalledIntegrationsCredentialLeak()` 對 PROJECT_INDEX + SESSION_HANDOFF + SESSION_LOG 三個 surface 強制 grep

### 2. 四類整合嘅紀律差異

#### 2.1 Connectors（Anthropic 官方 vetted）

Anthropic 官方 directory 嘅 ready-to-use MCP server（譬如 Notion / Slack / Linear / Google Drive / Atlassian / HubSpot / 等）。用戶經 Claude Desktop Settings → Extensions → Browse 一鍵安裝，credential 自動加密儲存喺 OS Keychain / Credential Manager。

紀律：
- AI 可使用 `mcp__<connector_name>__*` tool 直接 read / write
- Write operations 必 read-back verify 後才聲稱成功（沿用 `packs/knowledge.md` Rule 6 紀律）
- Auth 失敗（token expired / revoked）即 surface「請開 Claude Desktop Settings → Extensions → 重新 authenticate」+ 唔嘗試自動 fix

#### 2.2 MCPs（community / custom）

非 Anthropic 官方 vetted 嘅 MCP server，譬如 community 開發、用戶自建。需要 manual config（譬如 `~/.config/claude-code/mcp.json`）。

紀律：
- 用 `mcp__<server_name>__*` tool（同 Connectors 一樣 namespace）
- 因為非官方 vetted，AI 對 write operation 加倍小心：destructive writes 必先 dry-run + 用戶 confirm（沿用 `packs/safety.md` Rule 1）
- Server 失靈（process crash / config error）即 surface「請檢查 MCP config + 重啟 AI tool」+ 唔嘗試自動 fix

#### 2.3 Plugins（Claude Code plugin bundle）

distribution format，bundle = Skills + MCP server config + hooks。用戶經 `/plugin` command 安裝。

紀律：
- AI 唔需要 separately invoke plugin —— plugin 自身會 register 它嘅 skills + MCP servers
- 若 plugin 提供 skill，AI 按 skill 觸發條件自動 invoke（同 system skill 紀律一致）
- 若 plugin 提供 MCP server，當 Connector / MCP 處理（見 2.1 / 2.2）

#### 2.4 Skills（SKILL.md instruction set）

content format，由 Plugin 攜帶或 user-level / project-level 直接安裝。

紀律：
- AI 喺對話過程 detect skill 觸發條件（明示 keyword 或 implicit signal）即自動 invoke
- Skill 內容屬 instruction overlay，與 rule pack 紀律 layer 共存
- 若 skill 與 rule pack 紀律有 conflict，rule pack（safety / governance 等）優先

### 3. Source-of-truth Architecture（多層持久化組合）

當項目用多個整合構成 source-of-truth 架構（譬如 Notion DB Index + 本機真源 + Google Drive 參考檔），AI 必先讀 `dev/PROJECT_INDEX.md` `## Installed Integrations` `### Source-of-truth Architecture` sub-table，識別每層分工：

| Layer | 角色 | Write Direction |
|-------|------|-----------------|
| 真源（source of truth） | 原始可審計嘅 reference 內容 | 由用戶手動置入；AI 不直接寫入 |
| Index | 登記每份真源檔嘅 metadata + 摘要 + tag | AI 經 Connector 直接讀寫 |
| 持久化參考檔（mirror） | 防本機 disk failure / 跨裝置 access | 用戶手動同步；AI 唔自動 push |
| Working draft | AI 寫 task output | AI 直接 read + write 本機檔 |

每個 Layer 由邊個 Integration 承擔由 PROJECT_INDEX schema 明示。AI 唔可越層（譬如將 Index 當真源、將 Working draft 直接 push 上 mirror）。

### 4. Cross-session Lifecycle（6 階段）

#### 階段 0 — First-contact declaration（onboarding 階段）

新手用戶第一次 trigger phrase 後，onboarding pack（`dev/rules/onboarding.md`）Scenario A-E Step 1 加 micro-question 或 Scenario F dedicated path 引導用戶 declare 已裝整合。

#### 階段 1 — Initial recording

用戶答完，AI 寫入 PROJECT_INDEX `## Installed Integrations` 4 個 subsection（Connectors / MCPs / Plugins / Skills）+ 必要時填 Source-of-truth Architecture sub-table 描述多層分工。

#### 階段 2 — Cross-session handoff

`dev/SESSION_HANDOFF.md` `## Durable Anchors` section 必含「項目登記表 Installed Integrations section 必讀」reference；next-session opening message 嘅 read order 已 cover PROJECT_INDEX（既有第 6 項）。

#### 階段 3 — Startup availability probe

新 AI session 開工讀 PROJECT_INDEX 後，對每個 declared Integration 跑 minimal capability probe（譬如 Notion 試 `mcp__notion__search`、Drive 試 `mcp__google-drive__list`）。

- Probe success → update `Last Verified` cell + 進入正常 task loop
- Probe fail（current AI tool 冇裝 / auth expired / network 問題）→ startup card warn 一句「⚠️ Boundary: Notion Connector declared 但 mcp__notion__* unavailable，will fallback to paste flow」；用戶決定點處理

#### 階段 4 — Task execution（knowledge pack Rule 5 配合）

`packs/knowledge.md` Rule 5（v0.3.0 重寫）紀律由本 pack 接力 enforce：先 check declaration → functional 用直接 MCP → unavailable fallback paste + drift flag → undeclared but referenced ask user。

#### 階段 5 — Mid-session drift handling

任務做到一半 Integration 失靈（Notion auth 過期 / rate limit / network timeout）：

- AI 即時 surface 失敗 + 建議用戶 re-auth（讓用戶自己處理 credential issue）
- AI 唔嘗試自動 fix auth
- 更新 PROJECT_INDEX `Last Verified` cell + 加 note 紀錄 drift event
- Closeout 時 SESSION_LOG 紀錄 drift narrative，handoff 提示下次開工 verify

#### 階段 6 — Multi-tool 環境 cross-tool 一致性

用戶可能 Claude Code session 用 Notion MCP → 收工 → 下 session 用 Codex（可能未裝 Notion MCP）：

- PROJECT_INDEX declaration 屬 project-level，唔 lock 一個 AI tool
- 新 AI session 開工自動 verify availability（階段 3）
- 若新 AI tool 冇相應 MCP：startup card warn + fallback paste；用戶決定 (i) 跨 tool 統一裝 / (ii) 接受 capability difference / (iii) 切返有裝嘅 tool

## Rules

1. **Credential 機密分離**：AI 不要求用戶喺對話貼 credential；識別 credential prefix 即 redact + warn rotate；寫 PROJECT_INDEX 前 self-check 無 credential leak。
2. **Declaration before use**：任務涉及外部工具前，先讀 `dev/PROJECT_INDEX.md` `## Installed Integrations`；無 declaration 即 ask user about Integration status，唔自己假設未裝。
3. **Connector-first default**：當 declared Integration functional，優先使用直接 `mcp__*` tool call；paste fallback 只當 Integration unavailable 時。
4. **Write operations read-back verify**：所有外部 write（Notion create-page / Drive upload / Slack post 等）必 read-back 對齊後才聲稱 success。
5. **No auto-fix credential / auth issues**：Auth 失靈即 surface 俾用戶處理（指向 AI 工具設定界面），AI 唔嘗試自動 fix。
6. **Cross-tool capability awareness**：新 session 開工 verify availability；若 current AI tool 冇相應整合，startup card warn + fallback。
7. **Source-of-truth layer 唔越界**：真源層 AI 不直接寫；Index 層 AI 經 Connector 讀寫；Mirror 層用戶手動同步；Working draft 層 AI 直接 read/write 本機。
8. **Drift event mandatory recording**：任何整合失靈 / unavailable 即更新 PROJECT_INDEX `Last Verified` cell + SESSION_LOG drift narrative + handoff next-session prompt 提示。
9. **Plugin / Skill 紀律 subordinate**：若 Plugin 攜帶 Skill 觸發，與 rule pack 紀律 layer 共存；conflict 時 rule pack（safety / governance / closeout）優先。

## Checks

- 開工 verify `dev/PROJECT_INDEX.md` `## Installed Integrations` section 存在 + 4 subsection schema 完整
- 開工對每 declared Integration 跑 capability probe，update `Last Verified` cell
- 任何 mid-session Integration drift 即 surface + 紀錄
- Closeout 前確認 `Last Verified` cell 已 update 為今次 session 結果
- Credential leak self-check 對 PROJECT_INDEX + SESSION_HANDOFF + SESSION_LOG 任何 write
- Cross-reference verify：PROJECT_INDEX External Sources `via` column 引用 entry 必喺 Installed Integrations subsection 命中

## Closeout

收工時：

1. 更新 PROJECT_INDEX `## Installed Integrations` 嘅 `Last Verified` cell 為今次 session 嘅 verify 結果
2. 若 session 中發生 drift event，SESSION_LOG entry 必含 drift narrative + 影響 + 建議下次處理
3. SESSION_HANDOFF `## Risks / Blockers` 列任何未解決嘅 Integration 失靈
4. Next-session opening message 提示「下次開工先 verify <integration> auth」若上 session drift 未解
5. 若 session 中新加 Integration（用戶 mid-session declare），確認已寫入 PROJECT_INDEX + cross-reference External Sources `via` column

## Anti-pattern（不要做的事）

| Anti-pattern | 點解唔做 | 正確做法 |
|---|---|---|
| 用戶提到 Notion / Google Drive 即假設冇 Connector，直接列 paste packet | 違反 2026-05 reality：Connector ecosystem 已成熟，paste-only fallback 不應係 default | 先 read PROJECT_INDEX Installed Integrations；無 declaration 即 ask user about Integration status |
| 將 credential value 寫入 PROJECT_INDEX / SESSION_HANDOFF / SESSION_LOG | 違反機密分離原則 + git history 永久保留泄露 | Credential location 只記指向（譬如「Claude Desktop Extensions」），永不記 value |
| 用戶喺對話貼 credential value，AI 直接 用 / 紀錄 | 違反 enforcement Rule 1 + 用戶可能誤泄露 | 即時 redact + warn 用戶 rotate token + 解釋機密分離原則 |
| Auth 失靈即嘗試自動 fix / re-auth flow | 越界（屬 AI tool + 用戶範圍）+ 可能引入 credential exposure | Surface 失敗 + 指向 AI 工具設定界面 + 唔自動 fix |
| Connector 寫入後唔 read-back verify | Write 可能 silently fail（rate limit / partial write）—— 用戶以為 success | 必 read-back verify 後才聲稱 success（沿用 knowledge Rule 6） |
| 跨 layer 越界（譬如 AI 將 Working draft push 上 Drive mirror） | 違反 Source-of-truth architecture 分工 + 可能 corrupt 真源 | 嚴守 PROJECT_INDEX 嘅 Layer 分工 |
| 新 AI session 開工唔 verify availability，直接按舊紀錄假設可用 | Stale state risk —— token 可能過期、AI tool 可能切換 | 開工必 probe + update `Last Verified` |

## Cross-reference

- `packs/knowledge.md` Rule 5：Connector-first 紀律 enforcement，本 pack 接力
- `packs/safety.md` Rule 12：Credential leak prevention，本 pack 機密分離原則 implementation
- `packs/onboarding.md` Scenario F：first-contact declaration 入口
- `runtime-core/AGENTS.core.md` Section 1：startup probe 紀律
- `runtime-core/PROJECT_INDEX.md` `## Installed Integrations` + `## External Sources` `via` column：declaration registry
