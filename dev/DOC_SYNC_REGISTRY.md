# Doc Sync Registry

Purpose: map change types to documents and checks. Keep this as rows, not long prose.

## Status Vocabulary

Use: `confirmed`, `unverified`, `pending`, `blocked`, `not_applicable`.

| Change type | Also check/update | Verification |
|---|---|---|
| New file or directory | `dev/PROJECT_INDEX.md` Directory Map | path listed |
| Generated Markdown or durable artifact | `dev/PROJECT_INDEX.md` Directory Map / Fact Base / Entry Points, and this registry when future updates need sync | artifact classified as indexed / synced / temporary / one-time evidence; duplicate source-of-truth risk checked |
| Stack or command change | `dev/PROJECT_INDEX.md` Stack / Entry Points | command verified or marked unverified |
| Public behavior change | README, public docs, changelog | docs mention current behavior |
| API or SDK behavior change | API docs, examples, tests | tests or documented reason |
| Runbook change | runbook path in `PROJECT_INDEX.md` | procedure still executable |
| Governance rule change | relevant pack/core, registry, README if public-facing | complexity budget checked |
| Closeout/startup contract change | `AGENTS.md`, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`, `dev/PROJECT_INDEX.md`, README quick usage | opening message schema + workspace identity present |
| Workspace identity change | `dev/SESSION_HANDOFF.md`, `dev/PROJECT_INDEX.md` | root/branch/commit/status recorded or marked unverified |
| Release | release notes, README version, changelog | release pack checklist |

## Registry Rule

If a change has no matching row, add a row before closeout or record why no durable sync rule is needed. At closeout, record sync status for every row touched by the session.

## Session Sync Status

Recorded at closeout per the Registry Rule above. Newest first.

### 2026-09-07 — S216（Agent Handoff Kit v0.3.29 → v0.3.66 升級）

| Row touched | Status | Note |
|---|---|---|
| Governance rule change | `confirmed` | `AGENTS.md` managed core、八個 rule pack、`RULE_PACKS.md` 均由官方 v0.3.66 更新；複雜度預算由 Kit 自身管理，本項目未新增自訂 core 規則。 |
| Closeout/startup contract change | `confirmed` | `AGENTS.md` §4 契約更新；`dev/SESSION_HANDOFF.md` 補回 `Validation / QC`、`Risks / Blockers` 兩節與 `Reconstruction evidence`；`START_NEXT_SESSION_PROMPT.txt` 由 handoff 唯一 fenced block 重生並經 prompt mirror check 讀回。opening message schema 與 workspace identity 均在。 |
| Workspace identity change | `confirmed` | `dev/PROJECT_INDEX.md` `## Workspace Identity` 已按 S216 唯讀 git 探針更新 branch/commit（`6cb80c6`，領先六個）、未提交摘要（17 檔），並新增兩行：Kit 檔案版本控制缺口、根目錄平行安裝。 |
| New file or directory | `confirmed` | `dev/rules/closeout.md` 與 `dev/governance_migrations/2026-09-07T18-23-33-046Z-*/` 已記於 `dev/PROJECT_INDEX.md`。 |
| Public behavior change | `not_applicable` | 本節零程式碼、零檢索、零產品行為改動。 |
| API or SDK behavior change | `not_applicable` | 同上。 |
| Release | `not_applicable` | 未 commit、未 push、未部署。 |

**跨檔 blocked 項（`dev/DOC_SYNC_CHECKLIST.md`）**：row「Governance rule change (AGENTS.md)」與「New governance file added to install」要求同步 `INIT.md` FILE 1 mirror，狀態 **`blocked`**。理由：`INIT.md`（1,036 行，2026-05-10）鏡像的是 package 化之前的 AGENTS.md 結構（§4a／§5a／§11a），Agent Handoff Kit v0.3.66 核心沒有這些章節，機械同步會產生錯誤鏡像。解封條件：先決定 `INIT.md` 是否已退役。已開為 `dev/SESSION_HANDOFF.md` `Open Priorities` ⑦。
