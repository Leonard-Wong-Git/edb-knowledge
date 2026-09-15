# Project Index

Purpose: give a stateless AI a compact map of the project before it reads or edits files.

## Stack

| Field | Value | Last verified |
|---|---|---|
| Agent Handoff Kit template version | 0.3.66 | package prototype |
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
| `backend/` | Node.js/TypeScript backend（Channel B 搜尋 API、Render 部署、OpenAI node-fetch + Node 22.x；`backend/.env` = Supabase service key，勿入 git）。**Render 環境變數：`OPENAI_MODEL`（合成器，現為 `gpt-4o-mini`，只可在 dashboard 確認）、`JUDGE_MODEL`（S211 新增，判斷閘專用，程式預設 `gpt-4.1-mini`，Render 無須設定）。、**`MAX_PER_SOURCE`（S226 新增，量度用：未設＝現行公式 `max(2, ceil(top_k/3))`，設了就覆寫每來源配額。生產刻意不設 —— 實測放寬到 8 是來源層 −4 換片段層 +5 的一換一）**。**`GET /health` 自 S211 起回報 `commit`（Render 注入嘅 `RENDER_GIT_COMMIT` 前 7 位，本機為 `local`）同 `started_at`——部署是否落地由此判斷，不必再開 dashboard | backend / 部署任務 |
| `app.html` / `index.html` / `mobile.js` / `mobile.css` | 公開前端（`PLATFORM_VERSION` 常數在 `app.html`；GitHub Pages @ policychecker.wongfu.net） | 前端任務 |
| `dev/source/channel_a_coverage.py` + `CHANNEL_A_RETIREMENT_LEDGER.tsv` + `CHANNEL_A_COVERAGE_FINDINGS.md` | **Channel A 退役量度**（逐條事實 → 文件語料覆蓋 + 已核實出處）。落手前必讀 FINDINGS：機械判定嘅 tier 有 44% 撐唔住人手覆核 | Channel A 退役 / 鏡像 chunk 相關任務 |
| `dev/source/eval_retrieval.py` + `eval_queries.json` + `eval_runs/` | 檢索 eval harness（39 條短 query，打 live endpoint）。**S212 加片段層**：每條 query 記 `chunk_ids`，`expect_text_any` 以文字簽名斷言（**唔用 chunk id——id 係 text 嘅 md5，每次重切全源改晒**），片段層獨立於來源層判分，因為同一批來源可以換咗答到問題嗰段。**任何檢索改動必須一對 before→after**；改前先確認個集覆蓋到你要動嗰個維度 | 檢索 / 路由 / 門檻改動 |
| `dev/source/judge_acceptance.py` + `judge_acceptance_cases.json`（frozen 35）+ `judge_transplant_fresh_s202.json`（fresh held-out 10）+ `judge_prompts/`（v3 shipped / v4a·v4b candidates）+ `judge_runs/` | anti-confab judge 驗收 harness。`--cases`/`--cache` override 可獨立計分 held-out 集（frozen 不污染）；**judge 係 LLM 非決定性，任何 verdict 要 ≥3 runs**；量前 dashboard reconfirm `OPENAI_MODEL`。findings＝`JUDGE_PROMPT_FINDINGS.md` | judge / synthesis-gate 改動 |
| `dev/source/route_regression.mjs` | 路由回歸測試（46 條 query，覆蓋每條現有路由），並直接由真源抽取 `SOURCE_SETS` 驗關鍵來源成員資格。直接由 `searchChannelB.ts` 求值真正 regex／allowlist，不另寫平行定義。另設「已知缺口」區塊：路由不到但非本次造成者只報告、不影響退出碼 | 改 `TOPIC_KEYWORDS`、`SOURCE_SETS` 或新增路由 |
| `dev/source/vault_lead_delta.mjs` | vault-lead bypass 規則改動嘅確定性量度。judge 與 synthesis 皆為未設 temperature 嘅 LLM 呼叫，同一組 case 連跑兩次結果不同；此腳本不呼叫 LLM，只用確定性嘅檢索分數算出 `forcedLeads`、舊規則所看嘅 slot 0 與新規則所看嘅 mainLead，只報 bypass 判斷真正改變嘅 case | 改 `VAULT_LEAD_SCORE` 或 bypass 判斷邏輯 |
| `dev/source/cache_drift.mjs` | 量度 `judge_acceptance` 凍結 chunk cache 與今日真檢索嘅距離。2026-09-01 實測 35 條有 9 條 top-5 已不同，`D00_s177_frozen_post` 只餘 1/5 重疊——對該 9 條而言 harness 量緊一個不存在嘅檢索狀態 | 引用 judge 驗收數字前；決定是否 refresh cache 時 |
| `dev/source/qc_report.py` + `qc_report.json` + `status-07cc7942c0.html` | **知識庫品質健康檢查（S212）**。21 項檢查覆蓋全庫，答四條問題：政策指唔指得清楚、片段合唔合標準、有冇切得太碎或太粗、質素量唔量得到。契約與通告系統的 `qc_report.json` 相同。門檻用**基準值不用零**，而且**等於基準報 WARN 不報 PASS**——仍在服務中的缺陷不是綠燈。`--self-test` 有多條專證閘會紅的斷言。頁面新鮮度在瀏覽器端算，管線死了頁面自己轉紅 | 想知全庫現況；封版前；改任何入庫／切片邏輯之後 |
| `dev/source/release_gate.json` | **封版標準（S212）**。`qc_report.py` 讀此檔算 `releaseGate`。未有 waiver 的 WARN 一律 NOT_MET（預設是擋）；waiver 要 owner／reason／`accept_until`，過期自動失效；六項人手檢查沒有日期簽核就是 NOT_MET 不是「不存在」；`NOT_MEASURED` 等於 NOT_MET。**出廠 waiver 為空、人手項目全部未驗，所以閘現時 FAIL 7/15——這是真實狀態** | 決定可否封版；接受某個 standing WARN 時 |
| `dev/source/check_registry_drift.py` + `registry_drift.md` | **登記／庫存／瀏覽清單三者對不上的地方（S212，Open Priority ②）**。五類：ZOMBIE（已退役仍服務）、SERIES_UNMONITORED（registry 用年度樣式描述、三個監察都不展開年份）、UNMANAGED（庫內有片段但從未登記）、PHANTOM（可瀏覽但零片段）、UNLISTED（搜得到但瀏覽不到，人手策展佇列）。**只有 ZOMBIE 退出碼非零**——對清不完的佇列亮紅燈會被靜音 | 想知瀏覽清單追唔追得上；策展前 |
| `dev/source/registry_series.py` | **一行 registry 代表整個年度系列時的共同答案（S222）**。`stat_enrolment_report` 用 `url_primary_pattern` + `years_extracted` 描述 13 份文件，而店內以 `stat_enrolment_2012…2024` 分片。純函式：`monitor_rows()` 對普通行回傳自己（identity），對系列行展開成逐年行。`check_freshness`／`check_expiry`／`check_source_titles`／`check_registry_drift` 四者共用 —— id 推導只此一份，唔會有第二個答案 | 改任何「一行代表多份文件」的登記邏輯前 |
| `dev/source/check_pgvector_release.py` + `pgvector_seen.json` | **第七個監察（S222）**：盯 `supabase/postgres` 的 `nix/ext/versions.json`，等 Supabase 打包 pgvector **≥0.8.4**（HNSW 解封門檻）。**靜默設計** —— 只有跨過門檻、或上游檔案結構變咗（監察瞎咗）先出聲；0.8.3 落地只寫入 state 檔不作聲 | 想知 HNSW 幾時解封；改門檻或上游路徑時 |
| `.github/workflows/backend_build_check.yml` | **編譯閘（S223 建，S224 改為可阻擋）**：跑 `npm ci` → `check` → `build` → `route_regression` → `execute_ingest --self-test`，紅了就開／更新一個 Issue，綠了自動關閂。存在理由：2026-09-13 Option A watcher 推出不編譯的 `main`，**八個 workflow 無一個跑 typecheck**，Render 建置失敗後繼續服務舊 build，`/health` 照報 `ok:true`，部署凍結 16 小時無徵狀。🔴 **不得加回 `paths:` 過濾** —— required status check 要求該 commit 報 success／skipped／neutral，而 `paths:` 過濾的 workflow 對不命中的 commit **甚麼都不報**，該 check 會永遠 pending 並永久擋死那次 push。路徑範圍改為在 job 第一步 `Scope` 內判斷（watched：`backend/**`、`execute_ingest.py`、`route_regression.mjs`、本 workflow 自己），判不到就傾向照跑；scope 略過的 run 不會關閂 breakage issue（它甚麼都沒有編譯）**S224：已經係 `main` 的 required status check**（ruleset `main build gate`，id 23311105）—— 直接 push 到 main 會被拒：`Changes must be made through a pull request` ＋ `Required status check "build-gate" is expected`（實測）。唯一 bypass 係 **DeployKey**：個人帳戶 repo **不能**豁免內建 GitHub Actions（GitHub 回 `Actor GitHub Actions integration must be part of the ruleset source or owner organization`），所以四條會 commit ledger 的監察 workflow（`discover_check` / `freshness_check` / `pgvector_check` / `qc_report`）改為 `actions/checkout` 帶 `ssh-key: ${{ secrets.LEDGER_DEPLOY_KEY }}` 經 SSH 推。四者都不碰 `backend/`，所以豁免它們不會漏走這道閘要守的東西；而 deploy key 的 push **仍然會觸發 workflow**（`GITHUB_TOKEN` 的不會），所以它們照樣被 scope-skip 秒速放行 | 改 `backend/**`；想知點解 main 紅咗；改動任何會 push 的 workflow 時 |
| `dev/source/eval_runs/2026-09-14_s223_kgecg_g29_overlap.json` | **`kgecg_2017` vs `g29` 覆蓋率重量（S223）**：推翻 S222「只覆蓋 84.5%」的證據檔。含方法（同一抽取器＋剝離 page marker／空白／數字＋30 字視窗）、**對照組（自己對自己 0 miss）**、雙向對稱落差（11.7%／11.3%）、以及把落差視窗拆半的分解（88.5% 接合處產物 → 真正獨有 **0.91%**）| 有人再提「兩份 KG 指引各有獨有內容」時；想抄這套對照組方法去比較任何兩份文件時 |
| `dev/source/check_monitor_health.py` | **監察本身的看門狗（S222）**。由 GitHub Actions run 歷史（唔係自寫台帳 —— 台帳要由可能已崩潰嗰次 run 自己寫）判斷每個監察最後一次**成功**幾時；過咗週期自動 `workflow_dispatch` 補跑，靜超過兩個週期或連續失敗先開 Issue。**「讀唔到」係第三種狀態**，唔會摺成「從未成功」而出一份假全紅。改任何排程 workflow 都要同步它的 `WORKFLOWS` 表 | 監察疑似冇跑；加減排程監察時 |
| `dev/_s213_corpus.py` + `_s213_validate_gold.py` + `_s213_build_gold_staffing.py` | **Gold set 的標籤來源與守門（S213）**。`_s213_corpus.py` 是唯一准許取得 passage signature 與頁碼的途徑，內含兩個後端移植：`dominant_page`（`searchChannelB.ts:1054`，因為 **`wiki_chunks` 沒有 `page` 欄**，頁碼是查詢時由 `=== Page N ===` 標記推導）與 `clean_for_match`（`searchChannelB.ts:1089`，回傳前會剝走頁碼與章節標記，含標記的簽名永遠對不上）。三者比對前一律 **NFKC fold**（語料有 868 條相容表意文字 chunk）。`_s213_validate_gold.py` 對每條標籤獨立重新推導，不通過即隔離不修 | 建立或修改 gold set 標籤 |
| `dev/_s213_run_gold.py` + `_s213_eval_metrics.py` + `_s213_gold_all.json` | **檢索準確度量度（S213/S214）**。Active gold 現為 185 條；S214 把兩條失效 NCS 移至 deprecated audit、加入兩條 replacement，並把校董雙重事項拆成兩題。歷史 162／184 題 artifacts 仍保留原分母，不得用新 gold 回寫舊結果。指標：Source Recall@1/3/5/8、Chunk Recall@1/3/5、MRR、同源霸位、逐字重複佔位、無答案題三分類、禁引曝露、分範疇與分 split。**缺 chunk assertion 時回傳 NaN 而非 1.0** | 量度檢索準確度；比較排序策略 |
| `dev/source/gold_deprecated_s214.json` | S214 deprecated gold audit：完整保存舊 `ss_ncs_chinese_framework_missing`／`ss_ncs_history_adapted`、失效原因及 replacement ID；不納入 active gold glob | Gold 血緣與歷史追溯 |
| `dev/_s214_rank_model.py` | **Channel B overlay 排序的純模型與規格（S214）**。`merge_current`／`merge_exact_only`（＝已落地生產嗰個）／`merge_proposed`（Gate 1 否決咗嘅全窗 score sort，保留作反例）＋ T1–T14 共 41 條斷言。**`origin` 只用於 overflow 優先序與測試，永不可進入顯示排序 key**（Gate 1 defect D1）。`--fidelity` 對真實生產輸出重放，三態退出碼：`NO_EVIDENCE`=2（一條都冇驗到，**不可讀成通過**）／`FAIL`=1／`PASS`=0。**Gate 2B 用 TypeScript 實作時，TS 版必須通過同一批斷言 —— 本檔是規格，不是拋棄式工具** | 改排序／overlay／合成窗邏輯 |
| `dev/_s214_gate2a1_replay.py` | **離線 CURRENT vs 變體重放（S214）**。只計真正可導出的指標，導不出就標 `NOT_COMPUTABLE` 而非推測。兩種 artifact schema 分開處理：parallel-array（184 題 gold run，可全算）與 nested-`results`（九題探針，**無 gold label，Source／Chunk Recall 不可計**）。`acceptable_alternatives` 由 `dev/_s213_gold_all.json` 讀入（184 條中 26 條有），不作近似 | 比較排序策略；驗證排序改動 |
| `dev/source/footnote_lead_probe.py` | S196 註腳 lead 驗收 harness。**S214 加 `window_of()` 記錄完整 top-8**（id／source_id／content_type／score），舊欄位零改動故向後相容。正向 = 每條註腳自己嗰題必須保住 lead；負向 = plausible-gap。⚠️ **正負 `lead_score` 分佈重疊**（正向下限 0.6061 vs 負向上限 0.7213）→ **純提高門檻在數學上分不開兩個母體** | 改註腳 lead 門檻或排序前必跑 |
| `backend/supabase/s214_route_first_candidate.sql` + `backend/scripts/routeFirstProbe.ts` | **S214 Phase B route-first 候選**。SQL 為獨立命名的 `match_wiki_chunks_routed`（先按 route allowlist 過濾再精確向量排序，刻意 seq scan，`set local enable_indexscan/bitmapscan = off`），**獨立命名以避開 S116 的 PGRST203 overload 事故**；同一段 DDL 亦已併入 `backend/supabase/schema.sql` §6b。**S215 零列探針實測：函式已存在於 live schema**，但函式本體無法由 PostgREST 核實、安裝者與授權無記錄、線上 build 引用次數為 0。呼叫方 `wikiRepository.searchWikiRoutedExact()` 由 `FEATURE_ROUTE_FIRST_SEARCH`（預設 `0`）閘住，失敗回退舊 ANN，並對 `57014` 做最多三次限定重試 | 改 route 過濾、向量排名或任何 Supabase RPC DDL；**動 DDL 前必先 INSPECT live 定義** |
| `backend/scripts/routeFirstGold.ts` + `dev/_s219_score_before_after.py` | **S219 route-first 全 gold before／after 閘**。TS 端 in-process 呼叫 `searchChannelB()`（不起伺服器，繞開 `server.ts` 10/min 限流；同一 query 的 embedding 兩邊共用，令唯一變數只有 flag），只輸出原始結果 JSONL；判分交回 `_s213_run_gold.score_item`，**不在 TS 重寫一套判分**。關鍵儀測：逐次記錄 `match_wiki_chunks_routed` 的 HTTP status —— `searchChannelB.ts:1481` 的 `catch {}` 會把失敗的 routed RPC 靜默吞掉，令「靜默退回」與「flag 跑過但無改變」在結果上完全相同，不分開就會讀成假通過。分四類：routed／partial（先敗後成，延遲問題）／silent-fallback（全敗）／no-route。**56 條 no-route 題可作噪音底線控制組**（S219 實測為 0） | 任何 route 過濾或排序改動的 before→after；驗收任何被 `catch {}` 包住的候選路徑 | **【S220 改良】** 加記全庫 RPC 耗時（此前只記 routed，而修正後兩邊的分別正在於全庫 RPC 跑不跑）；輸出檔名改為 `--label` 可指定（原本寫死 s219 檔名，重跑會覆蓋前一節證據）。
| `backend/scripts/_s220_retryBudget.ts` + `dev/_s220_latency_verdict.py` | **S220 兩支判讀工具。** 前者離線 stub `fetch` 驗證 57014 重試的時間預算（冷啟動重試保留／預算用盡不再試／非 57014 即時失敗／快速連續超時仍可三次），零網絡零 live 讀取；後者由 gold 跑的逐次 RPC 耗時，在任意上限下**數**出失敗數，取代由 8 秒外推 3 秒的做法。 | 檢索延遲與重試相關任務 |
| `backend/src/lib/groundedSynthesis.ts` + `backend/scripts/groundedSynthesisRegression.ts` + `groundedSynthesisProbe.ts` | **S214 grounded synthesis 候選，預設關閉**。Structured Outputs draft → 確定性逐字引文核對 → 輸出衞生閘 → 獨立 judge → 只渲染全部通過的 claims；錯誤 fail closed。證據政策 A：只有 `vault_extract` 可支持答案。`--acceptance-affected` 精確跑受舊 harness 影響的 18 題，讀 active gold query、保存 evidence 原始 query 及 fingerprint，最高 36 次 HTTP；舊 40 題 mode 遇 deprecated NCS fixture 會 fail closed。Codex 每次執行前必先取得 Leonard 對服務／模型／最高次數的明確批准；Claude 不得執行 probe | 改合成、引文、棄權或 `llmClient` structured output |
| `dev/_s214_grounded_acceptance_report.md` + `dev/_s214_gold_abstention_review.md` + `dev/_s214_grounded_v3_review.md` + `dev/source/eval_runs/2026-09-05_s214_grounded_synthesis_probe_acceptance_v1.json`／`acceptance_v2.json`／`acceptance_v3_windowfix.json` + `2026-09-06_s214_fresh_retrieval_5.json` + `2026-09-06_s214_ncs_history_candidate.json` | S214 grounded synthesis 驗收證據。v1／v2 因 18／40 題舊 harness 選窗偏差而標示為 harness-confounded；v3 以修正窗重驗 18 題，25 次可核證 HTTP，無答案 9/9 棄權、可答 6/9 作答。其後 5 題 fresh retrieval 定位到 2 PASS／1 PARTIAL／2 FAIL；中史候選驗證證實 allowlist 修正只恢復 Source Recall，目標 Chunk Recall 仍失敗。現時 verdict=FAIL | Grounded synthesis QC／獨立覆核 |
| `dev/checklists/` | 15 域合規清單 + clauses（改後 re-run `gen_checklists_bundle.py`，勿手改 `checklists_bundle.json`） | 清單任務 |
| `dev/AUDIT.md` | S225 AI agent 架構與護欄盤點（`ai-agent-patterns` 既有系統路徑）。**凍結於 2026-09-14 的一次性評估，非 current state** —— 其中仍未解決者以 `SESSION_HANDOFF.md` `## Risks / Blockers` 與 `## Open Priorities` 為權威。碼有改動令結論失效時，更新此檔或明確標註作廢 | 檢討架構層級／護欄密度／量度缺口時 |
| `dev/_s214_route_first_focused_review.md` | 已保存三題 route-first before／after 的離線覆核；含交接與 RPC trace 落差、片段缺席、逾時及下一步限制 | 接續 Phase B 或考慮 live 驗證前 |

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

## Tool Operation References

Use this section for project-local runbooks or verified procedures for runtime-controlled tools such as browser validation, screenshots, DevTools, Playwright, crawlers, notebooks, desktop app automation, MCP/plugin helpers, or raw CLI/SDK operations.

Do not store credential values or machine-private paths here. Local machine-only references may be listed only when the project explicitly depends on them, and the scope / limits must say they are not portable.

| Tool / operation | Reference path or URL | Required before | Source and version/date | Scope and known limits | Last verified |
|---|---|---|---|---|---|
| TBD | TBD | TBD | TBD | TBD | TBD |
| Local HTML / app browser validation | TBD, for example project runbook or official browser-tool docs | Before validating local HTML, static app, generated guide, screenshot, click flow, or visual QA | TBD, include source and date | Prefer short-lived loopback localhost service when `file://` is blocked; record click/text/screenshot evidence and cleanup result; do not mutate user browser profiles or extension state | TBD |

## Local QC Commands

| Check | Command | Run before | Last verified |
|---|---|---|---|
| Channel A 覆蓋工具自檢 | `cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft" && python3 dev/source/channel_a_coverage.py --self-test` | 改覆蓋量度邏輯 | 2026-07-29 (S197) — 34/34 PASS |
| 檢索 eval 自檢 | `cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft" && python3 dev/source/eval_retrieval.py --self-test` | 改 eval 集或 harness | 2026-09-02 (S212) — ALL PASS（含片段層斷言，三條專證會紅）|
| 路由回歸 | `cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft" && node dev/source/route_regression.mjs` | 改 `TOPIC_KEYWORDS`、`SOURCE_SETS` / 新增路由 | 2026-09-14 (S224) — 46/46 query PASS + `chi_hist_jss_ncs_2019` curriculum 成員斷言 PASS |
| bypass 規則影響面 | `cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft" && node dev/source/vault_lead_delta.mjs` | 改 bypass 判斷 | 2026-09-01 (S211) — 只 3 個 case 改變，全部 want=能 |
| 凍結 cache 漂移 | `cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft" && node dev/source/cache_drift.mjs` | 引用 judge 驗收數字前 | 2026-09-01 (S211) — 26/35 相同、9 條漂移 |
| 知識庫品質檢查自檢 | `cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft" && python3 dev/source/qc_report.py --self-test` | 改任何檢查邏輯或基準值 | 2026-09-14（S225）— ALL PASS。S225 新增五條斷言守住「量不到不得報 PASS」，並以兩次針對性注入證明會轉紅（打回 `.get("FAIL", 0)` 默認 → 兩條轉紅；打回不過濾的 `sorted()[-1]` 選檔 → 選檔那條轉紅），其餘一條都沒受影響 |
| 產生知識庫品質報告 | `cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft" && set -a && . backend/.env && set +a && python3 dev/source/qc_report.py --check` | 封版前；改入庫／切片邏輯之後 | 2026-09-15（S226）— overall **ERROR**、**BLOCKER 0**、releaseGate **5/15** 達標（由 4/15；那 +1 是 `NO_UNMEASURED` 轉 MET，即量度覆蓋率，**不是質素**，沒有任何一格由紅轉綠）。兩項改動：`EVAL_CHUNK_LAYER` 由 `NOT_MEASURED` 轉 **FAIL**（`summarize()` 缺口修好）；**選檔改為優先生產端點**（Leonard 拍板選項 A），故 `EVAL_LATEST` 現量度自 `2026-09-15_s226_prod_gold.json` —— PASS **121**／FAIL 44／errors 1、chunk 58／107，detail 明寫「生產端點」並列出未被採用的較新非生產 run。**第三次重跑**（補傳 `series_monitored` 之後）：PASS 12 → **13**、ERROR 4 → **3**、`REGISTRY_SERIES` 由 FAIL 轉 **PASS**（那是閘漏傳參數造成的假 ERROR，非真缺陷）；releaseGate 仍 5/15 |
| 登記漂移自檢 | `cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft" && python3 dev/source/check_registry_drift.py --self-test` | 改漂移分類邏輯 | 2026-09-14（S225）— ALL PASS |
| 入庫 route-patch locator 自檢 | `cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft" && python3 dev/source/execute_ingest.py --self-test` | 改 `plan_route_patch`／`locate_route_block`／`live_route_patch`，或 `SOURCE_SETS` 結構有變 | 2026-09-14 (S223) — 13/13 ALL PASS（紅測：掛回舊 locator 則 6/13 FAILED）|
| 年度系列展開自檢 | `cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft" && python3 dev/source/check_freshness.py --self-test` | 改 `registry_series.py` 或四個監察任何一個 | 2026-09-14 (S222) — ALL PASS |
| pgvector 上架監察自檢 | `cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft" && python3 dev/source/check_pgvector_release.py --self-test && python3 dev/source/check_pgvector_release.py --prove-assertions` | 改門檻或上游路徑 | 2026-09-14 (S222) — ALL PASS ＋ 24 條證明會紅 |
| 監察看門狗自檢 | `cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft" && python3 dev/source/check_monitor_health.py --self-test && python3 dev/source/check_monitor_health.py --prove-assertions` | 加減排程監察、改 cadence | 2026-09-14 (S222) — ALL PASS ＋ 11 條證明會紅 |
| Gold set 標籤重驗 | `cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft" && python3 dev/_s213_validate_gold.py dev/_s213_gold_*.json --merge dev/_s213_gold_all.json` | 改動任何 gold 標籤之後 | 2026-09-15 (S226) — **184/185 通過，隔離 1**（`hr_appraisal`：錨點 `footnote_fn_sag_apx_coi_10_examples` 隨 S223 換版消失，**且該題簽名講收生／學生表現評核的利益衝突，與 query「教師評核」的 intent 不符，須 Leonard 重寫而非重錨**）。同批另一條 `cpd_mainland_promotion_tour` 已純機械重錨（簽名一字未改、全庫唯一命中、頁碼 188 → 191）。⚠️ 自 S213 之後到本節之前**從未重驗過**，因為驗證器要語料快取而預設路徑指向已消失的 scratchpad —— 該預設已於 S226 改為 repo 內路徑 |
| 檢索準確度量度 | `cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft" && python3 dev/_s213_eval_metrics.py --run <run.json> --gold dev/_s213_gold_all.json` | 任何檢索或排序改動的 before→after | 2026-09-15 (S226) — **生產實測**（`2026-09-15_s226_prod_gold.json`）：Source Recall **@1 0.442／@3 0.618／@5 0.691／@8 0.733**、Chunk Recall **@1 0.200／@3 0.309／@5 0.345**、MRR source **0.540**／chunk **0.255**。佔位：單一來源最多佔 5/8 格，15 條查詢有一個來源佔半數以上，逐字重複格位 0。無答案題 `WEAK_ANSWER` 18／**`CONFIDENT_WRONG` 1**。**禁引違規 8 條查詢**。最弱範疇 @1：gifted 0.111／curriculum 0.125／digital_education 0.200。（S213 舊值 R@1 0.364／Chunk R@5 0.273 是 162 題 gold 的數，題集與語料都已改，不可直接比） |
| 排序模型自檢（T1–T14） | `cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft" && python3 dev/_s214_rank_model.py --self-test` | 改排序／overlay 邏輯前後 | 2026-09-05 (S214) — 41 條 ALL PASS |
| 排序模型對生產重放 | `cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft" && python3 dev/_s214_rank_model.py --fidelity dev/source/eval_runs/2026-09-04_s214_gold_expanded_resolved.json` | 驗證模型是否仍反映生產 | 2026-09-05 (S214) — 180/184；餘 4 條成因已記於 Open Priorities ② |
| 註腳 lead probe 自檢 | `cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft" && python3 dev/source/footnote_lead_probe.py --self-test` | 改註腳 lead 邏輯前後 | 2026-09-05 (S214) — PASS |
| Grounded synthesis 離線回歸 | `cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft/backend" && npm run regression:grounded` | 改合成、引文核證、棄權或 Structured Outputs | 2026-09-06 (S214) — 48/48 PASS；生產與 probe 共用先篩一手文件、再取五格的 selector |
| Gold set 量度工具自檢 | `cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft" && for f in _s213_eval_metrics _s213_run_gold _s213_validate_gold _s213_build_gold_staffing _s213_fix_extract_headers _s213_title_backfill; do python3 dev/$f.py --self-test; done` | 改任何量度邏輯 | 2026-09-15 (S226) — 全部 ALL PASS（六支：`_s213_eval_metrics`／`_s213_run_gold`／`_s213_validate_gold`／`_s219_score_before_after`／`qc_report`／`check_registry_drift`）。S226 新增 12 條：`_s219_score_before_after` 5 條（含兩條守恆、一條「無斷言題目不得抬高 chunk 分母」），`qc_report` 7 條（選檔必須揀生產端點那一份）。**兩次紅測皆實證**：注入 `chunk_FAIL` 硬寫 0 → 3 條轉紅；注入選檔打回 `runs[0]` → 選檔那條轉紅；兩次還原後 `shasum -a 256` 皆與修補版相同 |
| route-first 全 gold before／after | `cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft/backend" && node_modules/.bin/tsx --env-file=.env scripts/routeFirstGold.ts` 然後 `cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft" && python3 dev/_s219_score_before_after.py --raw dev/source/eval_runs/<日期>_s219_route_first_before_after.jsonl` | 啟用 `FEATURE_ROUTE_FIRST_SEARCH` 之前；改 route 過濾邏輯 | 2026-09-15 (S226) — 185 題 12.4 分鐘、283 次 embedding、380 次請求、**errors 0、routeFailures 0**（S220 是 9）。來源層 119 → 122、片段層 chunk_PASS 54 → 58、routed p90 **2,498ms**（S220 8,335ms）、超過 8 秒 RPC 0（S220 18）、`no-route` 仍 56 題 |
| **生產 gold 實測（S226 新增登記）** | `cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft" && python3 dev/_s213_run_gold.py --gold dev/_s213_gold_all.json --out dev/source/eval_runs/<日期>_<節>_prod_gold.json` | 想知**生產實際**幾多分（非本機 in-process）；核實生產旗標狀態；封版前 | 2026-09-15 (S226) — 185 題約 32 分鐘（7 秒節流避開 10 req/min 限流）· 來源層 PASS **121**／FAIL 44／RECORD_ONLY 19 · **errors 1**（`sen_iep_intellectual` 撞 Supabase `57014` statement timeout —— 生產 anon 真上限 3 秒，本機用 service key 量同一批題是 0 錯，**低估幅度實測為 1 題**）· 片段層 chunk_PASS 58／chunk_FAIL 107 · 與本機旗標開啟側 **184/184 逐條同判**，故可用來核實 `FEATURE_ROUTE_FIRST_SEARCH` 的生產狀態 |
| **per-source 配額 A/B（S226 新增登記）** | `cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft/backend" && node_modules/.bin/tsx --env-file=.env scripts/_s226_capAB.ts --cap <N> --label <節>cap<N>` 然後 `cd "…/Draft" && python3 dev/_s219_score_before_after.py --raw dev/source/eval_runs/<日期>_<節>cap<N>_before_after.jsonl` | 改 `maxPerSource`／任何窗口配額邏輯之前；想知配額換了甚麼 | 2026-09-15 (S226) — 上限 3 → 8：來源層 PASS **122 → 118**（−4）、片段層 chunk_PASS **58 → 63**（+5）。**一換一，不應出貨**；結論是槓桿在同源內部重排（候選池已 over-fetch 40 條）。harness 自我核對：before 側與同日 in-process 旗標開啟側逐項相同。⚠️ 它不記錄 routed RPC，故計分器會印 `no-route 185`，非 route-first 失效 |
| Agent Handoff Kit doctor | `cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft" && npx --yes @adamchanadam/agent-handoff-kit@latest doctor --root .` | closeout / governance changes | 2026-09-07 (S216) — passed 53/53 @ v0.3.66 |
| Agent Handoff Kit closeout-status | `cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft" && npx --yes @adamchanadam/agent-handoff-kit@latest closeout-status --root .` | **v0.3.66 新增**：closeout 的語意閘，內含一次正式 doctor 讀回；nonzero 即 closeout blocked | 2026-09-07 (S216) |
| Agent Handoff Kit workspace-health | `cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft" && npx --yes @adamchanadam/agent-handoff-kit@latest workspace-health --root .` | **v0.3.66 新增**：唯讀 git 探針（root / branch / commit / worktree / 未提交） | 2026-09-07 (S216) |
| Agent Handoff Kit upgrade（預演） | `cd "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft" && npx --yes @adamchanadam/agent-handoff-kit@latest upgrade --dry-run --root .` | 升級前必跑；有 conflict 時 `--yes` 會**全數拒寫**（全有或全無），須先逐個人手合併 | 2026-09-07 (S216) |
| Project governance check | 見 `AGENTS.md` `<INSTRUCTIONS>` §3 (PLAN→READ→CHANGE→QC→PERSIST) + §4 closeout | closeout / durable file changes | 2026-06-22 (S176) |

## Workspace Identity

Record this at closeout so the next AI can detect wrong-root or workspace drift.

| Field | Value | Last verified |
|---|---|---|
| Expected project root | `/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft`（唯一目標；頂層 umbrella 只重定向至此） | 2026-06-22 (S176) |
| Git root | 同 project root（repo `Leonard-Wong-Git/edb-knowledge`；勿 set private） | 2026-06-22 (S176) |
| Branch / commit | `main` @ **`40ae3cf`**（S225 squash-merge PR #14）；**`HEAD == origin/main`，分歧 0/0**，工作區乾淨。判斷線上 backend 有無落後要**比檔不比 hash**：`git diff --name-only <部署commit>..HEAD -- backend` 是否為 0。⚠️ 本機另有舊分支 `claude/hopeful-gates-0efe44`（1 個 commit 未入 main，v1.5.0 年代），S225 未動 | 2026-09-14（S225） |
| Worktree or parallel workspace | 無 | 2026-06-22 (S176) |
| Uncommitted change summary | 無。S225 改動已合入 `40ae3cf`；生成檔 `dev/source/registry_drift.md` 與 main 一致。**`FEATURE_ROUTE_FIRST_SEARCH=1` 已於 Render 環境變數啟用（2026-09-09），該處只有 Leonard 改得到。** | 2026-09-14（S225） |
| 治理檔 git 狀態 | ⚠️ `dev/SESSION_HANDOFF.md`／`dev/SESSION_LOG.md`／`START_NEXT_SESSION_PROMPT.txt` 雖列於 `.gitignore` 但**實際已 tracked**（早於 ignore 規則 commit；git 唔會 untrack 已追蹤檔）→ 每次收工照常 commit（見 S173–S175 closeout commits） | 2026-06-22 (S176) |
| Kit 檔案版本控制缺口 | ⚠️ **S216 實測**：`AGENTS.md`／`CLAUDE.md`／`GEMINI.md` 三檔在 `.gitignore` 且**從未 tracked**（`git check-ignore -q` + `git ls-files --error-unmatch` 雙向實測）→ 升級對它們的改寫**不在版本控制內**，唯一還原點是 `dev/governance_migrations/<timestamp>/backup/` | 2026-09-07 (S216) |
| 平行安裝 | ⚠️ 專案根目錄 `/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/` 另有一份 **v0.3.24** 的獨立 Agent Handoff Kit（6 月起停滯，非 git repo）。**它不是本 repo 的一部分**，S216 按 Leonard 選擇零接觸。兩份版本不同，易撞混。 | 2026-09-07 (S216) |

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
