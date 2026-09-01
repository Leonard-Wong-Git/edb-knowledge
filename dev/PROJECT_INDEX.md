# Project Index

Purpose: give a stateless AI a compact map of the project before it reads or edits files.

## Stack

| Field | Value | Last verified |
|---|---|---|
| Agent Handoff Kit template version | 0.3.29 | package prototype |
| Runtime | TBD | TBD |
| Framework | TBD | TBD |
| Package manager | TBD | TBD |
| Test command | TBD | TBD |
| Build command | TBD | TBD |
| Deploy command | TBD | TBD |

## Directory Map

| Path | Role | Read when |
|---|---|---|
| `AGENTS.md` | primary Agent Handoff Kit entry and startup contract | session startup |
| `CLAUDE.md` | Claude Code bridge to the same startup path | Claude Code startup |
| `GEMINI.md` | Google Antigravity CLI / Gemini CLI migration bridge to the same startup path | Antigravity / Gemini startup |
| `START_NEXT_SESSION_PROMPT.txt` | auto-generated stateful startup prompt for the next local-agent session; `dev/SESSION_HANDOFF.md` remains authoritative | next session startup |
| `src/` | application source | coding task |
| `tests/` | tests | coding/QC |
| `docs/` | user or product docs | doc/public behavior change |
| `dev/` | governance state | startup/closeout |
| `dev/CODEBASE_CONTEXT.md` | **權威產品脈絡**（tech stack / directory map / External Services / Key Decisions）—— 本檔 Stack/Entry Points 等 TBD 欄勿重複填，以此為準 | coding / API task |
| `dev/PROJECT_MASTER_SPEC.md` | **權威長期規格**（架構 / runbook / release rules / §F locked decisions） | 架構或規格相關任務 |
| `backend/` | Node.js/TypeScript backend（Channel B 搜尋 API、Render 部署、OpenAI node-fetch + Node 22.x；`backend/.env` = Supabase service key，勿入 git）。**Render 環境變數：`OPENAI_MODEL`（合成器，現為 `gpt-4o-mini`，只可在 dashboard 確認）、`JUDGE_MODEL`（S211 新增，判斷閘專用，程式預設 `gpt-4.1-mini`，Render 無須設定）。**`GET /health` 自 S211 起回報 `commit`（Render 注入嘅 `RENDER_GIT_COMMIT` 前 7 位，本機為 `local`）同 `started_at`——部署是否落地由此判斷，不必再開 dashboard | backend / 部署任務 |
| `app.html` / `index.html` / `mobile.js` / `mobile.css` | 公開前端（`PLATFORM_VERSION` 常數在 `app.html`；GitHub Pages @ policychecker.wongfu.net） | 前端任務 |
| `dev/source/channel_a_coverage.py` + `CHANNEL_A_RETIREMENT_LEDGER.tsv` + `CHANNEL_A_COVERAGE_FINDINGS.md` | **Channel A 退役量度**（逐條事實 → 文件語料覆蓋 + 已核實出處）。落手前必讀 FINDINGS：機械判定嘅 tier 有 44% 撐唔住人手覆核 | Channel A 退役 / 鏡像 chunk 相關任務 |
| `dev/source/eval_retrieval.py` + `eval_queries.json` + `eval_runs/` | 檢索 eval harness（34 條短 query，打 live endpoint）。**任何檢索改動必須一對 before→after**；改前先確認個集覆蓋到你要動嗰個維度 | 檢索 / 路由 / 門檻改動 |
| `dev/source/judge_acceptance.py` + `judge_acceptance_cases.json`（frozen 35）+ `judge_transplant_fresh_s202.json`（fresh held-out 10）+ `judge_prompts/`（v3 shipped / v4a·v4b candidates）+ `judge_runs/` | anti-confab judge 驗收 harness。`--cases`/`--cache` override 可獨立計分 held-out 集（frozen 不污染）；**judge 係 LLM 非決定性，任何 verdict 要 ≥3 runs**；量前 dashboard reconfirm `OPENAI_MODEL`。findings＝`JUDGE_PROMPT_FINDINGS.md` | judge / synthesis-gate 改動 |
| `dev/source/route_regression.mjs` | 路由回歸測試（33 條 query，覆蓋每條現有路由）。直接由 `searchChannelB.ts` 求值真正嘅 `TOPIC_KEYWORDS`，**不另寫 Python 版本**——兩份定義會就 `\b`、量詞、`/i` 靜靜分岔。另設「已知缺口」區塊：路由不到但非本次造成者只報告、不影響退出碼 | 改 `TOPIC_KEYWORDS` 或新增路由 |
| `dev/source/vault_lead_delta.mjs` | vault-lead bypass 規則改動嘅確定性量度。judge 與 synthesis 皆為未設 temperature 嘅 LLM 呼叫，同一組 case 連跑兩次結果不同；此腳本不呼叫 LLM，只用確定性嘅檢索分數算出 `forcedLeads`、舊規則所看嘅 slot 0 與新規則所看嘅 mainLead，只報 bypass 判斷真正改變嘅 case | 改 `VAULT_LEAD_SCORE` 或 bypass 判斷邏輯 |
| `dev/source/cache_drift.mjs` | 量度 `judge_acceptance` 凍結 chunk cache 與今日真檢索嘅距離。2026-09-01 實測 35 條有 9 條 top-5 已不同，`D00_s177_frozen_post` 只餘 1/5 重疊——對該 9 條而言 harness 量緊一個不存在嘅檢索狀態 | 引用 judge 驗收數字前；決定是否 refresh cache 時 |
| `dev/checklists/` | 15 域合規清單 + clauses（改後 re-run `gen_checklists_bundle.py`，勿手改 `checklists_bundle.json`） | 清單任務 |

## Entry Points

| Entry | Path | Notes |
|---|---|---|
| App entry | TBD | TBD |
| Main config | TBD | TBD |
| Test suite | TBD | TBD |
| Runbook | TBD | TBD |
| Public docs | TBD | TBD |

## Fact Base

Reachable means the source can be found. It does not mean the source has been read in this session.

| Source | Role | Required before | Access method | Last verified |
|---|---|---|---|---|
| TBD | local source of truth / reference / draft / archive | TBD | path or instruction | TBD |

## External Sources

| Source | Role | Required before | Access method | `via` | Write-back rule | Last verified |
|---|---|---|---|---|---|---|
| TBD | source of truth / mirror / index / attachment store | TBD | URL, connector, or manual packet | `Notion Connector` / `Google Drive Connector` / `manual paste` / etc — must match an entry under `## Installed Integrations` | read-back required / manual only / no write | TBD |

> `via` column 紀律：每行 External Sources 必引用 `## Installed Integrations` 嘅 entry 名稱（譬如 `Notion Connector`、`Google Drive Connector`），確認該 source 經邊個 integration 訪問；無 declared Integration 嘅 source 用 `manual paste`。Cross-section consistency 由 doctor + qa:release 強制 enforce。

## Installed Integrations

> ⚠️ **機密分離原則**：本 section 只記錄 **項目使用紀錄** + **公開參考座標**（Notion DB 名 / URL / folder path 等），**絕對不記錄 API key / OAuth token / 任何 credential value**。Credential 應由 AI 工具自身 secure storage 管理（譬如 Claude Desktop Extensions 嘅 OS Keychain / Claude Code MCP config）。AI 寫入本 section 前必 self-check 確認無 credential leak；doctor 對本 section + SESSION_HANDOFF + SESSION_LOG 強制 grep credential prefix patterns（`sk-` / `ntn_` / `ya29.` / `xoxp-` / `ghp_` / `sl.` / `AKIA` / `AIza` 等）。

> 用途：新 AI session 開工讀本 section 知道項目可用嘅外部工具能力 + 各自分工。Declare 一次後跨 session AI 都會 leverage；每個 entry 必含 `Declared` + `Last Verified` 防漂移。

### Connectors（Anthropic 官方 vetted）

| Tool | Project Usage | Access Scope | Specific Instance | Credential Location | Declared | Last Verified |
|------|---------------|--------------|-------------------|---------------------|----------|---------------|
| TBD | TBD（譬如 DB Index 記真源 path / 持久化參考檔儲存） | read / read+write | TBD（譬如 DB 名 + URL / folder path） | TBD（譬如 `Claude Desktop Extensions`） | TBD | TBD |

### MCPs（community / custom）

| Server | Source | Project Usage | Credential Location | Declared | Last Verified |
|--------|--------|---------------|---------------------|----------|---------------|
| TBD | TBD（譬如 GitHub repo URL） | TBD | TBD（譬如 `Claude Code MCP config + env var`） | TBD | TBD |

### Plugins（Claude Code plugin bundle）

| Name | Bundle Content（Skills + MCP + hooks） | When Triggered | Last Verified |
|------|----------------------------------------|----------------|---------------|
| TBD | TBD | TBD | TBD |

### Skills（SKILL.md instruction set）

| Name | Source | When Triggered | Last Verified |
|------|--------|----------------|---------------|
| TBD | TBD（譬如 plugin bundle / user-level install） | TBD | TBD |

### Source-of-truth Architecture（多層持久化組合）

> 當項目用多個整合構成 source-of-truth 架構（譬如 Notion DB Index + 本機真源 + Google Drive 參考檔），本表描述每層分工，避免 AI 跨層越界。

| Layer | Surface（具體 instance） | Role | Write Direction |
|-------|--------------------------|------|-----------------|
| 真源（source of truth） | TBD（譬如 本機 `~/project/reference/`） | 原始可審計 reference 內容 | 用戶手動置入；AI 不直接寫入 |
| Index | TBD（譬如 Notion DB「Project Index」） | 登記每份真源檔 metadata + 摘要 + tag | AI 經 Connector 直接讀寫 |
| 持久化參考檔（mirror） | TBD（譬如 Drive folder「Project Reference/」） | 防本機 disk failure / 跨裝置 access | 用戶手動同步；AI 唔自動 push |
| Working draft | TBD（譬如 本機 `~/project/output/`） | AI 寫 task output | AI 直接 read + write 本機 |

## Local QC Commands

| Check | Command | Run before | Last verified |
|---|---|---|---|
| Channel A 覆蓋工具自檢 | `cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft" && python3 dev/source/channel_a_coverage.py --self-test` | 改覆蓋量度邏輯 | 2026-07-29 (S197) — 34/34 PASS |
| 檢索 eval 自檢 | `cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft" && python3 dev/source/eval_retrieval.py --self-test` | 改 eval 集或 harness | 2026-07-29 (S197) — ALL PASS |
| 路由回歸 | `cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft" && node dev/source/route_regression.mjs` | 改 `TOPIC_KEYWORDS` / 新增路由 | 2026-09-01 (S211) — 33/33 PASS |
| bypass 規則影響面 | `cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft" && node dev/source/vault_lead_delta.mjs` | 改 bypass 判斷 | 2026-09-01 (S211) — 只 3 個 case 改變，全部 want=能 |
| 凍結 cache 漂移 | `cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft" && node dev/source/cache_drift.mjs` | 引用 judge 驗收數字前 | 2026-09-01 (S211) — 26/35 相同、9 條漂移 |
| Agent Handoff Kit doctor | `cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft" && npx --yes @adamchanadam/agent-handoff-kit@latest doctor --root .` | closeout / governance changes | 2026-06-22 (S176) — passed 48/48 |
| Project governance check | 見 `AGENTS.md` `<INSTRUCTIONS>` §3 (PLAN→READ→CHANGE→QC→PERSIST) + §4 closeout | closeout / durable file changes | 2026-06-22 (S176) |

## Workspace Identity

Record this at closeout so the next AI can detect wrong-root or workspace drift.

| Field | Value | Last verified |
|---|---|---|
| Expected project root | `/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft`（唯一目標；頂層 umbrella 只重定向至此） | 2026-06-22 (S176) |
| Git root | 同 project root（repo `Leonard-Wong-Git/edb-knowledge`；勿 set private） | 2026-06-22 (S176) |
| Branch / commit | `main` == `origin/main` @ `d554b4c`（S197 closeout 前；closeout commit 後會前進一格） | 2026-07-29 (S197) |
| Worktree or parallel workspace | 無 | 2026-06-22 (S176) |
| Uncommitted change summary | S197 收工後全部 commit（無殘留）。⚠️ `dev/source/coverage_runs/` 係 gitignored（embed cache 14MB + 每個 run ~4MB，可由工具重生） | 2026-07-29 (S197) |
| 治理檔 git 狀態 | ⚠️ `dev/SESSION_HANDOFF.md`／`dev/SESSION_LOG.md`／`START_NEXT_SESSION_PROMPT.txt` 雖列於 `.gitignore` 但**實際已 tracked**（早於 ignore 規則 commit；git 唔會 untrack 已追蹤檔）→ 每次收工照常 commit（見 S173–S175 closeout commits） | 2026-06-22 (S176) |

## Change Hotspots

| Change type | Likely files | Required checks |
|---|---|---|
| API behavior | TBD | tests + docs sync |
| UI behavior | TBD | build + visual/manual check |
| Data model | TBD | migration/checks |
| Governance behavior | `AGENTS.md`, `dev/*` | doc sync registry |
| Closeout/startup contract | `AGENTS.md`, `START_NEXT_SESSION_PROMPT.txt`, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`, `dev/PROJECT_INDEX.md` | opening message present + workspace identity current + prompt file regenerated from handoff at closeout |

## External Services

| Service | Scope | Verification source | Last verified |
|---|---|---|---|
| TBD | TBD | TBD | TBD |

## Maintenance Rule

Update this file when stack, commands, directory roles, entry points, external services, workspace identity, durable runbooks, or governance file map changes.
