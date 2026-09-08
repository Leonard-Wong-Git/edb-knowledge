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

### 2026-09-08 — S218（起手探針節，零程式碼改動）

| Row touched | Status | Note |
|---|---|---|
| Workspace identity change | `confirmed` | `dev/PROJECT_INDEX.md` `## Workspace Identity` Branch / commit 列已由 `612e13e` 更新為 `0f8a7c9`，並註明 Render 報舊 commit 屬正常（零執行碼差異，`git diff --name-only 612e13e..HEAD -- backend app.html` = 0）。 |
| Closeout/startup contract change | `confirmed` | `dev/SESSION_HANDOFF.md` 五節狀態重寫（`Current Baseline` 1–2、`Validation / QC`、`Risks / Blockers` 1、`Open Priorities` 整段重生、`Last Session Record` 重生為 S218）；治理側兩項原文移入 `## Backlog`；`START_NEXT_SESSION_PROMPT.txt` 由開場白重生並 mirror 驗證。 |
| Release | `not_applicable` | 本節零 push、零部署、零 flag 啟用。 |
| Public behavior change | `not_applicable` | 零程式碼改動；生產跑的執行碼與 S217 部署那次相同（已實測 0 個檔差異）。 |
| Governance rule change | `not_applicable` | `AGENTS.md` 與 rule pack 本節未動。 |
| API or SDK behavior change | `not_applicable` | 無端點增減、無簽名改動。 |
| New file or directory | `not_applicable` | 無新檔。 |

### 2026-09-07 — S217（七個積壓 commit push 上主線並部署）

| Row touched | Status | Note |
|---|---|---|
| Release | `confirmed` | `42b1441..612e13e` push 至 `origin/main`；Render push-to-main 自動部署，`/health` 實測 `commit=612e13e`、`started_at` 19:26:49Z、`cache_a.warm` 455。推之前過齊 §3c 機器驗證閘（check 0 / build 0 / grounded 48-48 / route 46-46）。 |
| Workspace identity change | `confirmed` | `dev/PROJECT_INDEX.md` `## Workspace Identity` 的 Branch / commit 與 Uncommitted change summary 已按 S217 實測更新（`612e13e`，分歧 0/0）。 |
| Closeout/startup contract change | `confirmed` | `dev/SESSION_HANDOFF.md` 四節狀態重寫 ＋ `Last Session Record` 重生為 S217（S216 降級原文保留）；`START_NEXT_SESSION_PROMPT.txt` 由 fenced block 重生，mirror 逐位元組相等。原內容的頭號紅旗已成事實錯誤，故屬內容修正而非「為令 doctor 收聲而重生」。 |
| Public behavior change | `confirmed` | **本節初判 `not_applicable` 是錯的，Leonard 追問後逐個 hunk 核對已更正。** 本節雖零程式碼改動，但 push 令 S213/S214 的既有 commit 上生產：`searchChannelB.ts` 的 **establishment 路徑改動沒有任何 flag 保護、已生效**（觸發條件：staffing 路由 ＋ query 含「N 班」）。`regression:grounded` 那條斷言的範圍**只是合成 prompt**，不覆蓋整個系統，不足以支撐「零行為改動」。其餘執行碼已逐個 hunk 確認零行為改動。詳見 `dev/SESSION_HANDOFF.md` `## Current Baseline` 第 4 項與 `dev/SESSION_LOG.md` S217 第 8 點。 |
| Governance rule change | `not_applicable` | `AGENTS.md` 與 rule pack 本節未動。 |
| API or SDK behavior change | `not_applicable` | 無端點增減、無簽名改動。 |
| New file or directory | `not_applicable` | 無新檔。 |

| Session-log maintenance | `confirmed` | §4a 觸發（494 行 > 400）。`--self-test` 5/5 → `--apply`：494→197 行、8→3 條，5 條入 `dev/archive/SESSION_LOG_2026_Q3.md`。無損已驗證。 |
| Playbook 提案（§14） | `confirmed` | `inbox/2026-09-07-policychecker-flag-gated-not-behavior-neutral.md` ＋ `usage/policychecker.log.md` 一行 `lookup`。零接觸 trunk，已推上（`b0f69ec..8508a94`）。 |

**registry 補 row（`dev/DOC_SYNC_CHECKLIST.md`）**：本節改動類別「既有 commit 上主線並觸發部署（零程式碼改動）」在該檔無任何 row 匹配，按其 Anti-pattern guard **已先補 row 再繼續**，未靜靜略過。

**沿用 S216 的 blocked 項**：`INIT.md` FILE 1 mirror 仍然 blocked（OP ⑦），本節未觸及、狀態不變。

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

## S219 — 2026-09-08（185 題閘 ／ 根因調查 ／ overlay 暖機修復）

- `dev/SESSION_HANDOFF.md` — ✅ 已同步（Current Baseline 1–3、5 重寫；Validation 收攏為一段；Risks 第 2 項結案＋新增 5–7；Open Priorities 整段重生；Last Session Record 重生為 S219；開場白重生；State Reconciliation 加四段）
- `dev/SESSION_LOG.md` — ✅ 已同步（S219 條，含兩次自我推翻的 Fix Record）
- `dev/PROJECT_INDEX.md` — ✅ 已同步（新工具行、QC 指令行、Branch/commit、Uncommitted）
- `dev/CODEBASE_CONTEXT.md` — ✅ 已同步（`/health` 新增 `cache_b`、兩支新工具、AI Maintenance Log 兩條）
- `dev/DOC_SYNC_CHECKLIST.md` — ✅ **新增一登記行**（後端啟動期快取暖機／`/health` 狀態欄新增；原本無任何行涵蓋此類改動，依 §3 反模式守則先補行）
- `START_NEXT_SESSION_PROMPT.txt` — ✅ 由交接檔唯一 fenced 區塊重生並驗證逐位元組相等
- `backend/README.md` — ⚠ Skipped：本節未改 flag 行為；遺失的 5 行 flag 說明仍是 OP③，不在本節範圍
- Playbook usage — ✅ 兩行已 append（`throttled-api-not-empty-data` applied、`inspect-live-infra-before-ddl` lookup）

