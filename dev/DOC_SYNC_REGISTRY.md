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

## S226 — 2026-09-15（185 題 gold 重跑 ／ 片段層第一次量到 ／ 生產旗標行為核實）

命中 DOC_SYNC_CHECKLIST **row 60**（檢索準確度量度改動 —— 改了 `_s213_run_gold.py` 的匯總定義）與 **row 56**（品質檢查／封版閘改動 —— 該匯總令 `EVAL_CHUNK_LAYER` 由 `NOT_MEASURED` 轉為有數）。**未命中 row 44**（檢索 eval harness 改動）：`eval_retrieval.py`／`eval_queries.json` 一個字都沒動，query set 與 `expect_any` 斷言零改動。**未命中任何檢索改動 row**：`SOURCE_SETS`／`TOPIC_KEYWORDS`／`QUERY_EXPANSIONS`／門檻／spotlight 全部未改，`backend/src` 零改動。

- `dev/_s213_run_gold.py` — ✅ 改動本身（新增 `summarize()`，放在 `score_item` 旁邊作單一來源；本檔 run 的 `summary` 改為用它）。**未改任何判分規則**：`score_item`、NFKC fold、簽名比對逐字未動，故 row 60 的「改比對規則必同時改兩處」`not_applicable`。
- `dev/_s219_score_before_after.py` — ✅ 改為 `from _s213_run_gold import score_item, summarize`，刪去本地重複定義（33 行），新增 5 條斷言。
- `--self-test` 兩支 — ✅ `confirmed`，皆 ALL PASS（11 條／7 條）。**「先證它會紅」已做**：注入 `chunk_FAIL` 硬寫 0（即 S225 修掉的同族缺陷）→ 3 條轉紅；還原後 `shasum -a 256` 前後相同（`c1e3f57f…`）。
- `dev/_s213_gold_all.json` 標籤 — **未改**，故 row 60 的「改標籤必重跑 `_s213_validate_gold.py`」`not_applicable`。⚠️ 但**另有一項 `blocked`**：gold 標籤自 S223 SAG 換版後從未重新核實，`_s213_validate_gold.py` 要語料快取而預設路徑指向已消失的 scratchpad；5 條以 `g24` 為預期或替代來源者（`cpd_mainland_promotion_tour` 的 `verified_by.chunk_id` 指向已刪語料）現時無法對活語料重驗。判分本身走 source_id 與段落簽名、不靠該 chunk id，故不影響本節數字，但標籤新鮮度算**未驗**。
- `qc_report.json` — ✅ `confirmed`，已重跑 `--check` 並 commit（row 56 明文要求：靜態頁不重生等於改了邏輯而公開面仍是舊數）。逐行 diff 只有 12 加 13 減：`NOT_MEASURED` 1 → 0、`NO_UNMEASURED` NOT_MET → MET、`EVAL_CHUNK_LAYER` NOT_MEASURED → FAIL、releaseGate 4/15 → 5/15，其餘檢查零變動。
- `dev/source/qc_report.py` — **未改**。row 56 的「改基準值必同時改斷言」`not_applicable`。⚠️ **一項已知缺陷刻意未修**：`latest_eval_run()` 的選檔永遠揀旗標關閉側（見 HANDOFF Risks 9、Open Priorities ③(e)），因為「哪一份 run 代表生產」屬 release policy，須 Leonard 拍板；三個選項已寫入該處。
- `dev/PROJECT_INDEX.md` — ✅ `confirmed`。Local QC Commands 四行 `Last verified` 更新為 2026-09-15（S226）並附實測摘要；**新增一行**登記「生產 gold 實測」指令。更新後逐行核實表格分隔符數目未變（5 → 5，四行皆同），避免 S225 那個洗走原格內容的手法。
- `dev/SESSION_HANDOFF.md` — ✅ 已同步（`Current Baseline` 5 與**新增第 7 項**檢索準確度基線；`Validation / QC` 新增 S226 段；`Risks` 2(c) 結案改寫 ＋ **新增第 9 項**；`Open Priorities` ①②③ 與 Recommended next step 重寫）。marker 數目前後皆 35，H2 數目前後皆 67。
- **【第二批，Leonard 重建語料快取並拍板選項 A 之後】**
- `dev/_s213_gold_all.json` — ✅ 改了**一條**標籤（`cpd_mainland_promotion_tour`：`verified_by.chunk_id` 重錨、`expected_page` 188 → 191、note 寫明理由；簽名與 `expected_source_any` 一字未改）。**row 60 要求的重跑已做**：`_s213_validate_gold.py` 由 183/185 變 **184/185**。並已實證重錨對判分零影響（重跑計分器後兩側 summary 逐項相同，唯一 diff 是時間戳，已還原）。
- `hr_appraisal` — `blocked`（刻意）：錨點失效之外，**該題簽名講收生／學生表現評核的利益衝突，與 query「教師評核」的 intent 不符**，已開原文讀過兩個帶該段的片段。依 row 60「不通過即隔離，不可靜靜修好」維持隔離，等 Leonard 決定重寫 query 抑或換簽名。
- `dev/_s213_corpus.py` — ✅ `DEFAULT_CACHE` 由某一節 scratchpad 的絕對路徑改為 repo 內 `dev/source/.store_cache.json`，`S213_STORE_CACHE` 仍可覆寫，重建指令寫在常數旁邊。**這是 gold 標籤兩節沒重驗的機械根因。**
- `.gitignore` — ✅ 新增 `dev/source/.store_cache.json`（28MB 生成檔，等同語料副本，不得入 git）。已 `git check-ignore -v` 核實命中。
- `dev/source/qc_report.py` — ✅ 選檔改為優先生產端點（Leonard 拍板 **選項 A**）：新增 `measures_production()` 與 `eval_source_kind()`，`latest_eval_run()` 改為分流並回報所選檔是否生產、以及有無更新的 run 未被採用。**未動任何 `BASELINE` 值**，故 row 56 該項 `not_applicable`。新增 **7** 條斷言，紅測（選檔打回 `runs[0]`）準確轉紅，還原後 `shasum -a 256` 相同。
- `qc_report.json` — ✅ 已再重跑 `--check` 並 commit。`EVAL_LATEST` 現量度自 `2026-09-15_s226_prod_gold.json`（生產）：PASS 121／FAIL 44／errors 1；`EVAL_CHUNK_LAYER` 由 54/112 變 58/107。**閘計分零變動**（5/15、ERROR 4、`NOT_MEASURED` 0、overall ERROR）。
- `dev/PROJECT_INDEX.md` — ✅ 再更新四行 `Last verified`（`--check`、標籤重驗、準確度量度、工具自檢），逐行核實分隔符數目仍為 5。
- 六支工具自測 — ✅ `confirmed`，全部 ALL PASS。本節共新增 **12** 條斷言、做過 **2** 次紅測。
- `dev/SESSION_LOG.md` — `pending`：留待收工寫入（AGENTS.md §4 要求 log 條目在 closeout 寫）。
- `START_NEXT_SESSION_PROMPT.txt` — `pending`：同上，收工由開場白區塊重生。
- 外部同步 — `not_applicable`：零 Supabase 寫入、零 DDL、零公開契約改動（`knowledge.json`／`guidelines.json` 未動，`FREEZE_CONTRACT` 仍 PASS）、零 Render 設定改動、零 flag 改動。外部呼叫只有 `text-embedding-3-small` 283 次與 185 次唯讀生產搜尋。

## S225 — 2026-09-14（AI agent 架構盤點 ／ 修好封版閘一項假綠）

命中 DOC_SYNC_CHECKLIST **row 21**（New project doc added）與 **row 56**（品質檢查／封版閘改動）。row 56 的五項要求逐項對帳如下。

- `dev/source/qc_report.py` — ✅ 改動本身（`is_gold_eval()` ＋ 選檔過濾 ＋ 判分守衛 ＋ 五條斷言）。**未動任何 `BASELINE` 值**，故 row 56 的「改基準值必同時改斷言」一項 `not_applicable`。
- `qc_report.py --self-test` — ✅ `confirmed`，ALL PASS。**「先證閘會紅」已做**：兩次針對性注入，(a) 打回 `.get("FAIL", 0)` → 兩條絕對值斷言轉紅；(b) 打回不過濾 `sorted()[-1]` → 只有選檔那條轉紅；兩次後皆以 `shasum -a 256` 核實還原。
- `qc_report.json` — ✅ `confirmed`，已重跑 `--check` 並 commit（row 56 明文要求：靜態頁不重生等於改了邏輯而公開面仍是舊數）。合併途中每日 cron 亦推過一次，以「取 main 版本再用修補版重新生成」解決，未手動合併生成檔。
- `dev/source/check_registry_drift.py --self-test` — ✅ `confirmed`，ALL PASS。
- `dev/PROJECT_INDEX.md` Local QC Commands `Last verified` — ✅ `confirmed`，三行更新為 2026-09-14（S225），並附本次實測結果摘要。⚠️ 更新過程中一度把原有結果摘要洗走，已補回並逐欄核實表格結構未損。
- `.github/workflows/qc_report.yml` — `not_applicable`，本節無新增前置自檢。
- `dev/AUDIT.md` — ✅ `confirmed`（row 21）。已登記入 `dev/PROJECT_INDEX.md` Directory Map，分類為**一次性凍結評估、非 current state**；並在 `dev/DOC_SYNC_CHECKLIST.md` 新增其更新觸發（`backend/src` 的 LLM 呼叫／旗標／判官閘／護欄改動即須覆核）。
- `dev/SESSION_HANDOFF.md` — ✅ 已同步（`Current Baseline` 4；`Validation / QC` 新增 S225 段；`Risks` 第 8 項；`Open Priorities` ③ 與 Recommended next step；`User Environment` Git state；`Last Session Record` 轉 S225）。
- `dev/SESSION_LOG.md` — ✅ 已同步（S225 條）。
- `START_NEXT_SESSION_PROMPT.txt` — ✅ 由開場白區塊重生並逐字元讀回核實（fenced block 全檔唯一）。
- 外部同步 — `not_applicable`：本節零 Supabase 寫入、零公開契約改動（`knowledge.json`／`guidelines.json`／`K1_API_SPEC.md` 一個字都沒動）、零 Render 設定改動。

## S224 — 2026-09-14（閘由偵測變阻擋 ／ 入庫改行 PR ／ 四條監察搬去 deploy key ／ 修好一個假 BLOCKER）

命中 DOC_SYNC_CHECKLIST **row 29**（Option A 自動入庫管道改動）、**row 36**（Monitoring / CI workflow change，含「必須記錄新 CI secret 依賴」）、**row 55**（封版閘基準值改動）、以及**本節新增的凍結契約 row**。

- `dev/SESSION_HANDOFF.md` — ✅ 已同步（`Current Baseline` 第 4／6 點；`Validation / QC` 新增 S224 段；`Risks` 第 4 條由 🔴 降為 ⚠️ 並把新的 deploy key 風險併入其第 ① 點以守住 §4 上限 7；`User Environment` 新增 **Push 邊界**一段；`Open Priorities` 依 §4 重生 5 項；`Last Session Record` 重生為 S224，S223 原文完整下移；`Handoff Sufficiency Check` 重生並**順手消除兩行重複的 `Reconstruction evidence`**；開場白重生）
- `dev/SESSION_LOG.md` — ✅ 已同步（S224 條）＋ **結構修復**：S223 與 S222 原本被困在 Entry Template 的 ````markdown fence 內，已提出 fence 外、次序不變、零內容改動
- `dev/archive/SESSION_LOG_2026_Q3.md` — ✅ **§4a 觸發後歸檔**（S219–S215 五條，主檔 402 → 187 行；逐條對帳 10/10 剛好一份）
- `START_NEXT_SESSION_PROMPT.txt` — ✅ 由開場白唯一 fenced block 重生，**五個錨點全通過**（marker 唯一／fence 唯一／log 內無全文副本／正規化相等／byte-for-byte，4,924 bytes / 62 行）
- `dev/PROJECT_INDEX.md` — ✅ 已同步（`backend_build_check.yml` 那一 row 改寫，載明**不得加回 `paths:`** 的理由與 deploy key 機制）
- `dev/CODEBASE_CONTEXT.md` — ✅ 已同步（Option A 步驟 6 新形態；**新 CI secret 依賴 `LEDGER_DEPLOY_KEY` ＋ `MAIN_REPO_PAT` 需 Contents:RW **及** Pull requests:RW**；AI Maintenance Log 兩條）
- `dev/DOC_SYNC_CHECKLIST.md` — ✅ **新增「凍結對外契約四個值改動」row** —— 這是 `FREEZE_CONTRACT` 假 BLOCKER 的根因：本來沒有任何 row 指向 `qc_report.py` 的 `want` 字典
- `qc_report.json` — ✅ 重跑 `--check` 並 commit（row 55 要求：不重生等於改了邏輯而公開面仍是舊數）。BLOCKER 1 → 0
- `dev/source/ops/README.md` ＋ `APPROVALS_FORMAT.md` — **not_applicable**：`dev/source/ops/` 是 gitignored，該 secrets 契約改為寫入 ops repo `edb-knowledge-ops` 的 `executor.yml` 註釋（commit `5e27d2d`）
- `check_monitor_health.py` 的 `WORKFLOWS` 表 — **not_applicable**：`backend_build_check.yml` 無 schedule，不計入 cadence 契約；`--self-test` ALL PASS 確認表仍一致
- `README.md` ／ `CHANGELOG.md` ／ `app.html` ／ `PLATFORM_VERSION` — **not_applicable**：本節零用戶可見行為改動、零前端改動、零版本 bump
- Supabase ／ `source_registry.json` ／ 凍結 JSON 三檔 — **not_applicable**：零寫入、零接觸（`knowledge.json` 仍 2.3.0／455）
- ⚠️ **未同步（已知，留給下一節）**：`dev/CODEBASE_CONTEXT.md` 的 AI Maintenance Log **S211–S223 十三節從未補條目**（本節補了 S224 兩條）；repo root 那個 tracked 的 0-byte `main` 檔案未清（已向 Leonard 報告，未獲指示）

## S223 — 2026-09-14（部署管道解封 ／ SAG 換版合併 ／ kgecg 去重 ／ 推翻一個交接結論）

- `dev/SESSION_HANDOFF.md` — ✅ 已同步（`Current Baseline` 六行全重寫；`Validation / QC` 新增 S223 段；`Risks` 仍 7 項但第 2／4／7 項改寫、移除已解決的 `guidelines.json` 分歧、新增 python 環境分裂；`Open Priorities` 依 §4 重生 5 項；`User Environment` 加 python 三揀二與生產寫入權限更正；`Last Session Record` 重生為 S223，S222 原文完整下移；開場白重生。**無損檢查：42 個 `ack` marker 改前改後一致**）
- `dev/SESSION_LOG.md` — ✅ 已同步（S223 條，含一次推翻交接結論與一次自我更正的 Fix Record）
- `dev/PROJECT_INDEX.md` — ✅ 已同步（Directory Map 加 `backend_build_check.yml` 與 kgecg 覆蓋率證據檔兩行；Local QC Commands 加 route-patch locator 自測一條）
- `CHANGELOG.md` — ✅ 新增三條（v3.3.6 對數收尾、v3.3.7 手冊換版並合併、v3.3.8 KG 指引去重）
- `guidelines.json`（公開端點）— ✅ **不再 Skipped**：S222 列為 Risks 6 的分歧本節清掉了。以 `app.html` 的 `GUIDELINES_REGISTRY` 為真源逐條對齊，移除 7 條、同步 32 個欄位，158 → **151**，`_meta` **2.6.1 → 2.6.2**（Leonard 拍板）
- `knowledge.json` / `role_facts.json` / `dev/knowledge/role_facts.json` — ✅ 已同步（`_meta.stats.chunks` 兩次由 `live_total_count()` 讀真數後改；`_meta.stats.guidelines` 158 → 151；`_source_refs` 移除 `g24`。**`_meta.version` 2.3.0 與 `facts` 455 未動**）
- `app.html` — ✅ 已同步（PLATFORM_VERSION 3.3.5 → 3.3.8；`g24` 瀏覽條目移除、短名對照清理、`_source_refs` 清 `g24`；`sag_2025_11` 標題改 2026年8月版；片段數三處）
- `README.md` / `index.html` / `K1_API_SPEC.md` — ✅ 已同步（badge v3.3.3 → v3.3.8〔S222 漏了兩版〕、片段數、指引數 171 → 170、公開端點 158 → 151，含更新後的差異註腳）
- `dev/source/source_registry.json` — ✅ 已同步（`sag_2025_11` 換版 ＋「id 不追版次」註釋；`g24` 標 deprecated；`kgecg_2017` 與 `g29` 註釋寫入 S223 完整量度，並明寫 `kgecg_2017` **不要重新入庫**及其 checklist 用途）
- `dev/vault/sag_2025_11/extract_sag_2025_11_repaged.txt` — ✅ 已重抽（`repage_pdfs.py --write`，275 頁 275 markers）。⚠️ **驅動器沒有備份舊檔**（`PILOT_LEGACY` 指向一個已改名的舊檔案，legacy 計 0），舊 2025-11 版 extract 只存在於 git 歷史（`aeca54c` 之前）與本節 scratchpad
- `dev/CODEBASE_CONTEXT.md` — ⚠ **not_applicable**：本節零 tech stack／build／External Services 事實改動。⚠️ 但 **python 環境分裂**（預設 `python3` 無 `fitz`／`openai`）已寫入交接 `User Environment` 與 Risks 6 —— 若日後判斷它屬 Product/System 層，應由此檔承載
- `dev/DOC_SYNC_CHECKLIST.md` — ⚠ **not_applicable**：S222 剛加的三行已涵蓋本節兩類改動（上游原地換版、標籤與內容不一致）；本節無新類別需要登記
- `START_NEXT_SESSION_PROMPT.txt` — ✅ 由交接檔唯一 fenced 區塊重生並讀回驗證
- `backend/src` — ✅ 已同步（`searchChannelB.ts` 兩行位置修正；`wikiRepository.ts` alias 註釋改寫並**明寫為何刻意保留** `g24` alias）
- Playbook — ✅ 見本節 usage 行

## S222 — 2026-09-13／14（標籤錯配家族 ／ 監察看門狗 ／ 兩個生產寫入 ／ 三次自我推翻）

- `dev/SESSION_HANDOFF.md` — ✅ 已同步（Current Baseline 六行全重寫；Validation 新增 S222 段含「未做」六項；Risks **由 11 收斂為 7**；Open Priorities 重生並取消 S221 的 ①；Last Session Record 重生為 S222，**S221 原文由 git 取回完整下移**；Workspace Identity git 快照；開場白重生。無損檢查：42 個 ack marker 與改前一致）
- `dev/SESSION_LOG.md` — ✅ 已同步（S222 條，含三次自我推翻的 Fix Record 與證據處置）
- `dev/PROJECT_INDEX.md` — ✅ 已同步（Directory Map 加 `registry_series.py`／`check_pgvector_release.py`／`check_monitor_health.py` 三行；Local QC Commands 加三條自測）
- `dev/DOC_SYNC_CHECKLIST.md` — ✅ **新增三登記行**（上游 EDB 文件原地換版怎樣驗、標籤與它實際服務的內容不一致怎樣修、新增排程監察要同步 `check_monitor_health.py` 的 `WORKFLOWS` 表）。依反模式守則：前兩類本節撞到時登記冊無任何行涵蓋，先補行再處理
- `CHANGELOG.md` — ✅ 新增兩條（v3.3.4 g37 標籤／重複條目、v3.3.5 家族一次過修完）
- `README.md` — ✅ 已同步（in-app 指引數四處 177 → 171，含解釋 171 vs 158 差異的註腳）
- `app.html` — ✅ 已同步（PLATFORM_VERSION 3.3.3 → 3.3.5；GUIDELINES_REGISTRY 六條改標籤、六條移除；短名對照同步清理）
- `dev/source/source_registry.json` — ✅ 已同步（八條：六條標籤改正、`arts_kla_guide_2017` 與 `g31` 標 deprecated，全部附 S222 證據註釋）
- `guidelines.json`（公開端點，158 份）— ⚠ **Skipped（刻意）**：它同樣帶住 `g37` 舊標籤與 `arts_kla_guide_2017` 重複，但在**凍結合約**（`_meta` 2.6.1）之內，動它要 bump 凍結版本。已列入交接 Risks 6 待 Leonard 決定
- `dev/CODEBASE_CONTEXT.md` — ⚠ **not_applicable**：本節零 tech stack／build／External Services 改動；新增的是監察腳本，已入 `PROJECT_INDEX.md`（依 §0a 分層，監察屬治理側工具而非 External Services 事實）
- `START_NEXT_SESSION_PROMPT.txt` — ✅ 由交接檔唯一 fenced 區塊重生（49 行 / 4,427 bytes）並讀回驗證逐位元組相等
- `backend/README.md` / `backend/src` — ⚠ not_applicable：本節零後端改動
- Playbook — ✅ 兩行 usage（`freshness-monitor-test-served-url` lookup、`cloud-routine-vs-local-task` applied）＋ 新提案 `inbox/2026-09-13-policychecker-watchdog-for-cron-monitors.md`，已 commit 並 push（`3d41612`）

## S220 — 2026-09-09（route-first 次序修正 ／ 重試時間預算 ／ 全站文案對正 ／ OP② 生產解決）

- `dev/SESSION_HANDOFF.md` — ✅ 已同步（Current Baseline 全重寫；Validation 收攏為 S220 一段；Risks 重生 7 項；Open Priorities 依 §4 重生 5 項並移除兩項已完成；Workspace Identity 加生產 flag 狀態；開場白重生。無損檢查：H2 標題與 ack marker 與改前完全一致）
- `dev/SESSION_LOG.md` — ✅ 已同步（S220 條，含一次自我推翻的 Fix Record）
- `dev/PROJECT_INDEX.md` — ✅ 已同步（`routeFirstGold.ts` 行註明 S220 改良、新增兩支工具行）
- `dev/CODEBASE_CONTEXT.md` — ✅ 已同步（route-first RPC block：啟用狀態＋次序＋重試預算；另修正 S215 兩處已被交接推翻的記載；AI Maintenance Log 兩條）
- `START_NEXT_SESSION_PROMPT.txt` — ✅ 由交接檔唯一 fenced 區塊重生（71 行）並讀回驗證逐位元組相等
- `backend/README.md` — ✅ **OP③ 已完成**（S215 事故中失去的 flag 說明已由碼重寫；先查證 git 內無任何副本，commit message 明寫非還原）
- `CHANGELOG.md` — ✅ 新增 v3.3.3 條目
- 公開文案（`README.md` / `K1_API_SPEC.md` / `app.html` / `index.html` / `q.html` / `t-purchase.html` / `embed-sample.html` / `mobile.js` / 三個 JSON 鏡像）— ✅ 已同步（`sources` 288／120 → 300、指引 161／152 → 177／158、badge 3.3.0 → 3.3.3、幻影文案、休眠頁 noindex、八個快取鍵）
- `dev/source/execute_ingest.py` — ✅ **新增 `sources` 自動同步**（step 5c）；此前 display-sync 只同步片段數，來源數靠人手改故漂了四個月
- Playbook usage — ⚠ **不適用**：本節未 grep 全表、未開任何卡，按該庫規則不寫 usage 行。兩條可轉移教訓已備妥提案待交（見交接檔 Pending）

