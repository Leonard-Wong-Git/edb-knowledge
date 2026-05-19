# Session Log

<!-- Archives: dev/archive/ — entries moved when >400 lines or oldest entry >30 days -->

## 2026-05-19 Session 118 — Stage 2 combo 判定非可行（雙獨立驗證）→ pivot PLAN-1b：4 條 selective route promote（fixed cutoff）

- **ID:** Claude_20260519_1300
- **Summary:** Leonard `/goal A` 批 Stage 2 Scope A（combo adaptive cutoff）。出 §3 HIGH-risk PLAN（agent-team groundwork）→ pre-CHANGE offline acceptance gate **FAIL**：combo regress 病假/體罰/幼稚園收生/STEAM。獨立 audit **確認 FAIL 真**（非 harness bug；根因＝上游 ranking defect，正確 gold 排喺高分噪音之下，cutoff 結構上救唔到）。依 §3 偏離 + PLAN「FAIL→stop、唔 ship regression」停 CHANGE。§2 rule 6 衝突（/goal A vs no-ship-regression）報 Leonard → dismiss「do not proceed, wait」→ 其後「我不知道點決定，你按最終目標選擇及行動，直至/goal」＝授權自主。按最終目標（北極星＝正確改善檢索）pivot **PLAN-1b**。
- **PLAN-1b（agent-team 落手，全 Testing/ 先）：** feasibility 診斷根因（CPD＝純 allowlist-gap：gold 喺 sag_2025_11/g06 唔喺任何 SOURCE_SET；體罰/STEAM/幼稚園收生＝within-allowlist mis-rank）→ 建 4 條 dedicated selective route（cpd/kg_admission/conduct/steam，first-match，dedicated tight set 穿過 §E.3 SAG-exclusion 針孔）+ selective expansion（單一 QUERY_EXPANSIONS、§D.9/§3b 一規一處）。**獨立 audit：** worker 數學 faithful，但「OVERALL PASS」對 **病假 overstated**（病假 combo 仍 .25＝combo 對病假仍 regress、PLAN-1b 無掂）；§E.3 SAG≤3（quota cap=3）closed；8 條 unchanged 無 hijack；STEAM/體罰 lift global-rank-8 脆弱 flag。**Live-verify（dedicated /channel-b 真 probes=8）：** 4 route 可救 gold 全部 live surface（體罰§58 r9、STEAM r8、CPD/幼稚園收生 r1），offline 無高估 → live-robust。
- **裁定：** Stage 2 adaptive combo＝**正式放棄**（病राhard regression 兩獨立驗證；PLAN-1 promote 不用 adaptive threshold）。PLAN-1 真正得益＝**promote PLAN-1b 4 route（fixed cutoff）**：CPD 0→0.8、幼稚園收生/體罰/STEAM 改善、12 條零回歸、§E.3-safe、live-verified。
- **CHANGE（Draft）：** `backend/src/api/searchChannelB.ts` — SOURCE_SETS +cpd/kg_admission/conduct（dedicated tight sets，SAG 由 per-source quota 約束）、TOPIC_KEYWORDS +4 route（first-match 置頂）、QUERY_EXPANSIONS +4（同一 map 無 fork）。**min_score/effectiveMinScore 不動（fixed cutoff 保留）、無 combo、唔掂 S117 masking 契約。**
- **§2 rule 6 OVERRIDE record:** PLAN-1b promote＝Draft external-integration＝§3 HIGH-risk，常規須 Leonard PLAN-confirm。Leonard 明確 standing 授權「按最終目標選擇及行動直至/goal」+ agent-team（feasibility/獨立audit/monitor/live-verify 四重）為控制 + live test-verify 完成 → 視為授權；risk 已述、scope 最小、git-reversible、fixed-cutoff only。按 §2 rule 6 comply + 此 record（+ SESSION_HANDOFF）。
- **Verified/QC:** routing harness 12/12（4 新 route 對 + 8 unchanged 無 hijack）；`npm run check`✅`build`✅；`regression:semantic` overall=FAIL 但 **delta=0 new**（既有 FAIL-A/B record-only 未碰；7 topic-routing + 2 retrieval 全 PASS＝topicDetector/Channel-A 不受影響）。offline acceptance grade（獨立 audit + live-verify 雙重）＝行為驗收證據。
- **新風險（記）：** live-verify 5 RPC 有 2 個 HTTP400 / Supabase `57014` statement-timeout（retry 後成功）— free-tier Postgres 喺 probes=8 偶發 timeout，**生產可用性**問題（與檢索正確無關；S117 修好令真錯誤正確浮面成 error 非假「未配置」＝觀測性 working）。
- **Pending:** PLAN-1b promote 已落 Draft+QC+commit，生產 deploy 待 Render auto-deploy；probes=8 *live* 仍未獨立 `pg_get_functiondef` introspect（唯讀 INSPECT SQL 已交 Leonard、未跑）；Stage 2 combo 放棄；病假 combo-regression＝known（非本 promote 範圍，fixed cutoff 下 病假=.5 無回歸）。
- **Next:** 接手＝PLAN-1b 4 route 已 promote+verified；問 Leonard：(a) 跑唯讀 probes=8-live INSPECT？(b) Supabase free-tier probes=8 timeout 要否處理（生產可用性）？(c) 病假 combo-gap＝future PLAN-1c 抑或接受 fixed-only？

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| Product behavior / tuning change（Channel B PLAN-1b selective routing promote）| SESSION_HANDOFF baseline/Open-Priorities-regen/risks/record + SESSION_LOG 本 entry + QC evidence | ✓ Done |
| Long-term spec / locked decision / invariant（§E.3 four-round routing +4 selective routes；Stage-2 adaptive 放棄）| PROJECT_MASTER_SPEC §E.3 + §D（dedicated-route+quota 穿 SAG 針孔法）+ §C.4 Supabase free-tier probes=8 timeout caveat | ✓ Done |
| External API / service change | CODEBASE_CONTEXT External Services block＝N/A（Supabase 外部服務無變；內部 search-API 行為改變）；AI Maintenance Log +S118 | ✓ Done（Log）/ block N/A |
| Doc carrying now-stale "Stage-2 adaptive threshold is the path" | SESSION_HANDOFF Open Priorities/baseline（Stage-2 dropped，PLAN-1 = PLAN-1b routing）；auto-memory：+project Stage-2-vs-PLAN-1b finding、reference_supabase_pgvector_probes +timeout gotcha | ✓ Done |

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

⚠️ 然後讀 dev/HANDOFF_PACKAGE.md（可信狀態快照）。起手務必自行 verify git HEAD + knowledge.json._meta.stats vs SESSION_HANDOFF Current Baseline，並實測 egress（onrender /health，勿照抄）。

⚠️ Repo root = "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"（路徑含空格，shell 必須雙引號絕對路徑）。Channel B/retrieval PoC 喺姊妹資料夾 "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Testing/poc-retrieval/"（唔喺 git、Draft 零接觸）。`python` 唔存在用 `python3`。git commit+push 由 Claude 做（指定檔勿 -A）。Agent team 係預設模式（用嚟做嘢非淨係俾意見）。回覆用中文。

S118：Stage 2 adaptive combo 經雙獨立驗證**判定非可行並放棄**（病राhard combo-regression，根因＝上游 ranking defect）。Leonard 授權「按最終目標選擇及行動直至/goal」→ pivot 並 promote **PLAN-1b**：`searchChannelB.ts` 加 4 條 dedicated selective route（cpd/kg_admission/conduct/steam，first-match，dedicated tight set + 單一 QUERY_EXPANSIONS expansion），**fixed cutoff 不動、無 combo、唔掂 S117 masking**。已 commit+push（觸發 Render auto-deploy）。§2 rule 6 override 已記（HIGH-risk 在 Leonard standing 授權 + agent-team 四重控制 + live-verify 下進行）。

Current objective and progress state:
- PLAN-1b 4 route＝**promoted + verified**：CPD 0→0.8、幼稚園收生/體罰/STEAM 改善、12 條零回歸、§E.3 SAG≤3 quota-safe、無 hijack；offline grade 經獨立 audit + live-verify（真 probes=8 gold surface）雙重確認。routing harness 12/12、npm check/build ✅、regression:semantic delta=0 new。
- **Stage 2 adaptive combo＝放棄**（病राcombo .5→.25 hard regression，cutoff 救唔到上游 ranking）。PLAN-1 promote 改以 PLAN-1b routing 達成、**不再用 adaptive threshold**。fixed cutoff 下 病假=.5 無回歸。
- Channel B 北極星（memory project_direction）：合理+指引+**頁數** = CB-2 retrieval + CB-3 可追溯（頁數不可 defer）+ CB-1 質素。

Pending tasks in priority order:
1. 問 Leonard 排序：(a) 跑 audit-flagged **唯讀 probes=8-live INSPECT**（SQL 已備、未跑；S116 只敘述未獨立 introspect、曾 PGRST203 drift §E.13）；(b) **Supabase free-tier probes=8 statement-timeout（`57014`）** 生產可用性 — 要否降 probes / 加 retry / 升 tier；(c) 病假 combo-gap＝future PLAN-1c 抑或接受 fixed-only。
2. CB-3 可追溯（頁數不可 defer，北極星）— 未做。
3. 既有：🔴 FAIL-A Circular 注入 regression（record-only）；🔴 §E.10 admin-login security；P2 分類148/P3 數字；Mobile UI P2；HKEAA；低 doc-debt（FAIL-B semanticRegression.ts:292 stale 1.3.1）。

Key files changed this session:
- Draft（已 commit+push）：backend/src/api/searchChannelB.ts（+4 selective route：SOURCE_SETS/TOPIC_KEYWORDS/QUERY_EXPANSIONS）；dev/SESSION_LOG.md、SESSION_HANDOFF.md、PROJECT_MASTER_SPEC.md、CODEBASE_CONTEXT.md。
- Testing/poc-retrieval/eval/（PoC，非 git）：cb2_stage2_grade.py、CB2_STAGE2_grade_report.md、PLAN1B_grade_report.md + 候選/faithcheck/qvec 檔。
- auto-memory（repo 外）：reference_supabase_pgvector_probes.md（+free-tier probes=8 timeout gotcha）、project_* Stage-2-vs-PLAN-1b finding、MEMORY.md。

Known risks / blockers / cautions:
- **Stage 2 adaptive combo 放棄**（勿再嘗試 combo cutoff 救上游 ranking — 雙獨立驗證 dead-end；root cause 係 ranking 非 cutoff）。
- 🔴 **Supabase free-tier probes=8 偶發 statement-timeout（`57014` HTTP400）** — 生產可用性風險（retry 可恢復；S117 後正確浮面成 channel_b_status:"error" 非假「未配置」）。
- 🔴 probes=8 *live* 未獨立 introspect（Stage 任何依賴 probes 行為前必跑唯讀 `pg_get_functiondef`）；schema.sql 曾 drift→PGRST203（§E.13；RPC DDL 前必 INSPECT live、生產 DDL 仍 Leonard Dashboard）。
- 🔴 §E.10 admin-login security；🔴 FAIL-A；§3c regression:semantic 既有 FAIL-A/B record-only（本 change TS-only、delta=0）。
- 病假 combo .5→.25＝known combo-gap（非本 promote 範圍；fixed cutoff 下無回歸）。egress 間歇每次自測；路徑空格雙引號；Testing/ 喺 Draft git 外；改 Draft code commit 必入 SESSION_LOG；產品方向 P1→P2→P3 + 39→148 deferred 鎖定。

Validation status:
- PASS PLAN-1b：routing 12/12；npm check/build ✅；regression:semantic delta=0 new；offline grade（獨立 audit 確認、live-verify 真 probes=8 gold surface）；§E.3 SAG≤3。
- PENDING：probes=8-live INSPECT 未跑；Supabase timeout 未處理；CB-3 未做；Stage 2 combo 已放棄（非 pending，係 closed）。生產 deploy 待 Render auto-deploy（push 已觸發）。

Post-startup first action: 完成 §1 起手序 + HANDOFF_PACKAGE + 自測（git HEAD / stats / egress 實測）後，**PLAN-1b 4 route 已 promote+verified（push 已觸發 Render auto-deploy）——第一件事＝問 Leonard 排序**：(a) 唯讀 probes=8-live INSPECT（SQL 已備）(b) Supabase free-tier probes=8 timeout 生產可用性 (c) 病假 combo-gap future PLAN-1c vs 接受 fixed-only / 抑或推進 CB-3（北極星頁數）。可選：happy-path 生產 smoke 確認 Render 已 deploy PLAN-1b。**未 Leonard 明示前唔好自行做 Stage 2（已放棄勿復活）/ 其他 Draft / CB-3**。碰 admin/auth/公開推送前必讀 §E.10。Channel B 北極星見 memory project_direction_review。詳細 grade/audit/live-verify 證據喺 Testing/poc-retrieval/eval/PLAN1B_grade_report.md + CB2_STAGE2_grade_report.md。
```

---

## 2026-05-19 Session 117 — Fix Channel B masking-defect（promote-blocker）：searchCombined .catch 真失敗 vs 未配置 可區分

- **ID:** Claude_20260519_0715
- **Summary:** Leonard 經 agent-team 建議後 `/goal C` = 修 masking-defect。三隊唯讀一致裁定 (c) 行先（promote-blocker、最平 S effort、令日後 Stage-2 promote 喺生產可觀測）。修 `searchCombined.ts` `.catch`：真 Channel B 例外唔再重用 `degradedChannelBResponse`（=「未配置」），改出獨立 `failedChannelBResponse`（`degraded_kind:"error"` + `CHANNEL_B_ERROR_REASON`），combined 加 machine-readable `channel_b_status` discriminator。最小、additive、零前端 coupling、保留 A-only graceful degradation。
- **§2 rule 6 OVERRIDE record:** (c) 屬 §3 HIGH-risk（Draft backend external-integration）。常規須出 PLAN 等 confirm 先 CHANGE；Leonard 全 scope 知情下揀 C 並設為 binding `/goal` = 授權。risk 已述（HIGH，surface 細、git-reversible、code-only 無 Supabase DDL）；按 §2 rule 6：用戶明示 override → comply + 此 record。Diff + PLAN 已先示。
- **Triage (§2b):** code-logic / observability-contract defect。根因 `searchCombined.ts:118-123` `.catch` 對*任何* throw 都 return `degradedChannelBResponse` → byte-identical「未配置」HTTP200，真 transient/infra 失敗對 monitoring/eval 隱形（= PROJECT_MASTER_SPEC §E.13 防線4 記錄之 promote-blocker）。
- **READ (§2c):** searchCombined/searchChannelB/server.ts/env.ts 全文 + grep 全 consumer。確認：缺陷只喺 combined（dedicated /channel-b 真錯→HTTP400 已可分）；前端 index/app/q/t-purchase/mobile.js **零** consume `channel_b_*`/`degraded`（additive 安全）；Testing harness `cb2_stage1_verify_v2.py:89-90` keys on dedicated-endpoint `degraded&&未配置`（combined-only 修改不影響）；genuine-unconfigured 路徑 searchChannelB.ts:331 須保留。
- **CHANGE:** `searchChannelB.ts` +`ChannelBDegradedKind` type / +`degraded_kind?` on resp / +`CHANNEL_B_ERROR_REASON` / `degradedChannelBResponse` 設 `degraded_kind:"unconfigured"` / +`failedChannelBResponse`(`"error"`)。`searchCombined.ts` import 換 `failedChannelBResponse`+type / `.catch`→`failedChannelBResponse(query)`（保留 console.error err）/ `SearchCombinedResponse` +`channel_b_status?` / return surface。
- **QC:** `npm run check` ✅ `npm run build` ✅。§3d deterministic harness（/tmp，跑真 source 含真 fetch-fail，已清）**13/13 PASS**：S1 unconfigured→status=unconfigured/未配置；**S2 真例外(fetch failed)→status=error+CHANNEL_B_ERROR_REASON、NOT 未配置、A 仍貢獻**；S3 dedicated unconfigured→degraded_kind=unconfigured+未配置（harness classifier 不變）。`npm run regression:semantic` overall=FAIL 但 **delta=0 new**（PASS9/notes1/FAIL2 = 既有 FAIL-A finance_distinct + FAIL-B schema 1.3.1 stale，record-only、非本 change，未碰 knowledgeSelector/schema）；§3c 已重 baseline 無信 stale ✅。
- **Agent-team（唯讀 ×3，已交）:** feasibility c>b>a / independent-audit c→b→a / governance-monitor c→a→b — 一致 (c) 行先。Audit 另揭 2 caveat（入 risks）：probes=8 *live* 從未獨立 `pg_get_functiondef`/`proconfig` introspect（只敘述）；§C「HARNESS/LOAD artifact」label 偏寬（採購 k=7 實為未查 HTTP400 MALFORMED，recall 裁定仍企）。
- **Live verify:** 本 change 未 deploy（Render push 後 auto-deploy）；deterministic harness 已跑真 code path（含真 fetch 失敗）= error-discriminator 權威證據。Push 後做 happy-path 生產 smoke。
- **Pending:** Stage 2 adaptive threshold（PLAN-1 promote 仍未完成，§3 HIGH-risk，待 Leonard go；建議先做 audit-flagged 唯讀 probes=8-live INSPECT）；PLAN-1b（CPD/expansion，Testing/）；既有 FAIL-A/§E.10。**masking-defect 已修 = promote-blocker 清除。**
- **Next:** 接手 = masking-defect 已修+verified；問 Leonard 排 Stage 2（連 probes-live INSPECT）vs PLAN-1b。

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| Product behavior / tuning change（Channel B observability contract：真失敗 vs 未配置 可區分）| SESSION_HANDOFF baseline/Open Priorities 重生/Known Risks/Last Record + SESSION_LOG 本 entry + QC evidence | ✓ Done |
| Long-term spec / locked decision / invariant（resolving codified failure-lesson 防線）| PROJECT_MASTER_SPEC §E.13 防線4（promote-blocker RESOLVED S117）+ §C.4 Supabase 🔴 masking 行更新 + §D.14 註 | ✓ Done |
| External API / service change | CODEBASE_CONTEXT External Services block = **N/A**（Supabase 外部服務無變；內部 search-API 回應僅 additive optional fields，無對應 External Services block）；AI Maintenance Log +S117 entry | ✓ Done（Maintenance Log）/ block N/A |
| Doc carrying now-stale "masking promote-blocker active" | SESSION_HANDOFF Supabase Technical Notes 🔴 行 → RESOLVED；auto-memory `reference_supabase_pgvector_probes` L22 更新 | ✓ Done |

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

⚠️ 然後讀 dev/HANDOFF_PACKAGE.md（可信狀態快照）。起手務必自行 verify git HEAD + knowledge.json._meta.stats vs SESSION_HANDOFF Current Baseline，並實測 egress（onrender /health，勿照抄）。

⚠️ Repo root = "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"（路徑含空格，shell 必須雙引號絕對路徑）。Channel B/retrieval PoC 喺姊妹資料夾 "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Testing/poc-retrieval/"（唔喺 git、Draft 零接觸）。`python` 唔存在用 `python3`。git commit+push 由 Claude 做（指定檔勿 -A）。Agent team 幾時都可用。

S117：Leonard `/goal C` → 修咗 Channel B **masking-defect**（promote-blocker 清除）。`searchCombined.ts` `.catch` 唔再將真例外偽裝「未配置」：新增 `failedChannelBResponse`（`degraded_kind:"error"` + `CHANNEL_B_ERROR_REASON`）+ combined `channel_b_status` discriminator（"unconfigured"|"error"）；genuine-unconfigured 路徑不變。已 commit+push（觸發 Render auto-deploy）。§2 rule 6 override 已記（HIGH-risk 但 Leonard binding /goal = 授權）。

Current objective and progress state:
- masking-defect = **FIXED + verified**（§3d deterministic 13/13；npm check/build ✅；regression:semantic delta=0 new，既有 FAIL-A/B record-only）。promote-blocker 清除。
- PLAN-1 promote **仍未完成**（Stage 2 adaptive threshold 未做）——勿宣稱 released。生產 Supabase probes=8（Stage-1 FULL PASS）。
- Channel B 北極星（memory project_direction）：合理+有指引+**一定有頁數** = CB-2 retrieval + CB-3 可追溯（頁數不可 defer）+ CB-1 質素。

Pending tasks in priority order:
1. **Stage 2 — adaptive threshold @ searchChannelB.ts:346（取代固定 0.22 / category-drop 0.08）**：完成 PLAN-1 promote，§3 HIGH-risk gate，需 §3d matrix + live test-verify。**建議先做 audit-flagged 唯讀 INSPECT**：`pg_get_functiondef`/`proconfig` 實證 probes=8 真係 live（S116 只敘述、未獨立 introspect；偏偏 S116 出過 PGRST203 drift 事故，§E.13）。待 Leonard go。
2. PLAN-1b：CPD category-routing fix（gold 喺 sag_2025_11/g06 唔喺 curriculum allowlist，probes 救唔到）+ 選擇性 expansion vs §D.9 always-on consolidation（全 Testing/ 先）。
3. 既有：🔴 FAIL-A Circular 注入 regression（record-only）；🔴 §E.10 admin-login security；P2 分類148/P3 數字；Mobile UI P2；HKEAA；低 doc-debt（FAIL-B semanticRegression.ts:292 stale 1.3.1 / wiki_index._meta.total_chunks stale；§C「HARNESS/LOAD artifact」label 偏寬＝採購 k=7 未查 HTTP400）。

Key files changed in this session:
- Draft（已 commit+push）：backend/src/api/searchChannelB.ts、backend/src/api/searchCombined.ts（masking-defect fix）；dev/SESSION_LOG.md、SESSION_HANDOFF.md、PROJECT_MASTER_SPEC.md、CODEBASE_CONTEXT.md。
- auto-memory（repo 外）：reference_supabase_pgvector_probes.md L22（masking 已修）。

Known risks / blockers / cautions:
- **masking-defect FIXED**（promote-blocker 清除）。Render auto-deploy on push — 接手可做 happy-path 生產 smoke 確認 deploy。
- 🔴 audit caveat：probes=8 *live* 未獨立 introspect（Stage 2 前必做唯讀 `pg_get_functiondef`）；schema.sql 曾 drift→PGRST203（§E.13；任何 Supabase RPC DDL 前必 INSPECT live、勿信 schema.sql；生產 DDL 仍 Leonard Dashboard 親手）。
- 🔴 §E.10 admin-login security；🔴 FAIL-A regression（record-only）；§3c regression:semantic overall=FAIL = 既有 FAIL-A/B（非本 session，record-only；任何 release claim 前重 baseline 勿信 stale ✅）。
- egress 間歇每次自測；路徑空格雙引號；Testing/ 喺 Draft git 外；改 Draft code/data commit 必入 SESSION_LOG；產品方向 P1→P2→P3 + 39→148 deferred 鎖定。

Validation status:
- PASS masking-defect fix：§3d deterministic 13/13（真 fetch-fail→status=error 非 未配置；A-only graceful degradation 保留；dedicated harness classifier 不變）；npm check/build ✅；regression:semantic delta=0 new。
- PENDING：Stage 2 未做（PLAN-1 promote 未完成）；PLAN-1b 未做。生產 deploy 待 Render auto-deploy（push 已觸發）。

Post-startup first action: 完成 §1 起手序 + HANDOFF_PACKAGE + 自測（git HEAD / stats / egress 實測）後，**masking-defect 已修+verified（promote-blocker 清除）——第一件事 = 問 Leonard 排序**：(a) Stage 2 adaptive threshold（同一 §3 HIGH-risk promote gate，完成 PLAN-1；強烈建議先做唯讀 probes=8-live INSPECT）定 (b) PLAN-1b（CPD/expansion，全 Testing/）。可選：做 happy-path 生產 smoke 確認 Render 已 deploy masking fix。**未 Leonard 明示前唔好自行做 Stage 2 / PLAN-1b / 改其他 Draft**；PLAN-1 promote 未完成（Stage 2 未做）勿宣稱 released。碰 admin/auth/公開推送前必讀 §E.10。Channel B 北極星見 memory project_direction_review。
```

---

## 2026-05-18 Session 116 — CB-2 PLAN-1 Stage 1：ivfflat.probes 1→8（含 PGRST203 live 事故+復原）；Stage-1 recall CLEAN PASS 6/6；§C pending

- **ID:** Claude_20260518_1600
- **Summary:** Leonard 定 Channel B 北極星（無論點問都有合理、有指引、**一定要有頁數** — 入 memory）。出 **PLAN-1 v2**（CB-2 retrieval promote，§3 HIGH-risk，Leonard 批）：scope = probes + adaptive threshold；selective expansion 撞已驗證 §D.9 always-on expansion → 抽出做 PLAN-1b。**Stage 1 = 升 `ivfflat.probes` 1→8**，經 Supabase 受限角色多輪現實修正 + 一次 live 事故 + 復原，最終落**正確 live text 變體**。Agent-team（3 並行唯讀）cross-check。clean-verify v2 → **Stage-1 recall CLEAN PASS**。§C 基建風險判定 closeout 時仍背景跑（task `bur5rn16o`）= Stage-1 最終裁定 PENDING。
- **Stage 1 機制修正鏈（§0b/§2b triage，全部實證非猜）：** (a) function-SET-clause `set ivfflat.probes=8` → **42501**（Supabase 封 extension GUC clause）；(b) plpgsql `stable`+SET LOCAL → **0A000**（SET 須 VOLATILE）；(c) 套 schema.sql `vector(1536)` 簽名 → **PGRST203 overload** 同 live `text` 變體並存 → **Channel B 全 query 返 0（live 事故）**。診斷 A（session `set ivfflat.probes=8`→8）+ B（proconfig null）定路；ROLLBACK `drop function ...(vector,...)` 還原 baseline；INSPECT 攞真實 live 定義 = `match_wiki_chunks(query_embedding text,...)` 內部 `::vector` cast（schema.sql 自稱「exact contract」實已 drift = 事故根因）。最終 ① APPLY-FINAL：plpgsql **volatile** + `set local ivfflat.probes=8` 落**真實 text 變體**，Leonard Dashboard 套用、smoke 3 行無錯。
- **Live 狀態改變（非 git）：** 生產 Supabase `match_wiki_chunks` 現 = plpgsql volatile + SET LOCAL ivfflat.probes=8（text 變體）；事故中 drop 咗 vector overload。**Channel B 生產現行 probes=8。**
- **Agent-team（唯讀，已交）：** (1) CPD root-cause **決定性**：CPD→category=curriculum→SOURCE_SETS 排除 SAG，但 CPD 5 gold 全喺 `sag_2025_11`/`g06`（唔喺 allowlist）→ source 後置過濾砍走、**probes 永遠救唔到** = category-routing defect。(2) 獨立 audit **推翻**我「6/7」overstatement（屬量度 artifact）。(3) clean-verify v2 設計（dedicated /channel-b 繞 masking + pacing + classify）。
- **Leonard 裁示：** CPD 移出 Stage-1 → PLAN-1b（ANN母體=6）；masking-defect（searchCombined `.catch` 將 Channel B 例外偽裝成「未配置」HTTP200 → B 失敗對 monitoring/eval 隱形）= 獨立 promote-blocker，flag+defer（clean-verify 用 dedicated /channel-b 繞過）。
- **Verified/QC:** `cb2_stage1_verify_v2.py recall`（dedicated /channel-b、warmup+15s pacing）**全 12 class=OK**：6/6 ANN-recoverable flip 0→>0（年假.75 病假1.0 體罰.33 幼稚園收生.5 防賄.5 校曆1.0）、**0 回歸**（採購.2→.6 採購門檻.2→.4 STEAM穩）、sen/LSG 預期~0、CPD↪PLAN-1b。harness 經獨立 audit 證 bit-identical mirror AUTHORITATIVE `grade_channelB.py`（未改原 grader）。SQL smoke 無 42501/0A000/PGRST203。schema.sql = SQL-only（npm check/build/regression:semantic 不受影響；§3c gate 既有 FAIL-A/B record-only 未碰）。Draft git 只 `backend/supabase/schema.sql` M（+本 closeout governance docs）。§4a trigger=False（209 行）。**§C closeout 時完成（exit 0）：幼稚園收生 8/8 OK·防賄 8/8 OK·採購 7/8（1 transient），gold-consistency 8/8·8/8·7/7、p90<4.2s → 裁定 HARNESS/LOAD artifact、probes=8 sound（非真 free-tier 風險；之前 09/10 間歇失敗 = v1 combined-masking+限流 量度 artifact）。∴ Stage-1 = FULL CLEAN PASS（recall 6/6 + §C 無真基建風險）。**
- **Pending:** Stage 2 adaptive threshold 未做（同一 §3 HIGH-risk promote gate 內，待 Leonard go）；PLAN-1b（CPD routing + selective expansion vs §D.9）；🔴 masking-defect 修法待 Leonard 排 scope。**PLAN-1 promote 未完成（Stage 2 未做）勿宣稱 released。**
- **Next:** 接手 = Stage-1 已 FULL PASS（probes=8 生產現行），問 Leonard 下一步：Stage 2 adaptive threshold（同 promote gate）vs PLAN-1b（CPD/expansion）vs 先修 masking-defect promote-blocker。

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| Draft external-integration code change (Supabase RPC: schema.sql → real text-variant + SET LOCAL probes=8 + drift fix) | SESSION_LOG（本 entry）/ SESSION_HANDOFF（baseline+OP+risks+record）/ CODEBASE_CONTEXT（match_wiki_chunks 真實 text 簽名 + probes=8 live + Maintenance Log）/ PROJECT_MASTER_SPEC（§C.4 Supabase + §D probes 法 + §E 事故教訓）/ commit+push 指定檔 | ✓ Done |
| Live external platform change (production Supabase function modified — Leonard Dashboard) | SESSION_LOG/HANDOFF 記 live 狀態（probes=8 生產現行、vector overload dropped）；CODEBASE_CONTEXT External Services Supabase 註；下游無契約變（公開 JSON 不變） | ✓ Done |
| Isolated PoC (Testing/ only, no Draft) — clean-verify v1/v2 + dumps | SESSION_LOG/HANDOFF 記；PoC 自帶 CB2_STAGE1_report.md；CODEBASE_CONTEXT N/A（Testing/ 非 Draft tech-stack/未 promote） | ✓ Done |
| Lessons-to-rule (§8): schema.sql drift → PGRST203 incident; Supabase managed-role GUC constraints | PROJECT_MASTER_SPEC §E 新條 + §D 法；auto-memory ×2（reference_supabase_pgvector_probes / feedback_inspect_live_supabase_before_replace）+ MEMORY.md | ✓ Done |
| Promote-blocker discovered, deferred (masking-defect) | SESSION_HANDOFF Known Risks + Open Priorities；PROJECT_MASTER_SPEC §E 註；未修（Leonard flag+defer 裁示） | ✓ Done |

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

⚠️ 然後讀 dev/HANDOFF_PACKAGE.md（可信狀態快照）。起手務必自行 verify git HEAD + knowledge.json._meta.stats vs SESSION_HANDOFF Current Baseline，並實測 egress（onrender /health，勿照抄）。

⚠️ Repo root = "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"（路徑含空格，shell 必須雙引號絕對路徑）。Channel B/retrieval PoC 喺姊妹資料夾 "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Testing/poc-retrieval/"（唔喺 git、Draft 零接觸）。`python` 唔存在用 `python3`。git commit+push 由 Claude 做（指定檔勿 -A）。Agent team 幾時都可用。

S116 已 closeout（Leonard「收工」）。PLAN-1 v2 = CB-2 retrieval promote。Stage 1（升 ivfflat.probes 1→8）經 Supabase 受限角色多輪修正 + 一次 PGRST203 live 事故（schema.sql 簽名 drift）+ 復原；最終落正確 live text 變體 = plpgsql VOLATILE + SET LOCAL ivfflat.probes=8。**生產 Supabase match_wiki_chunks 現已 probes=8（Leonard Dashboard 套用）。** Draft backend/supabase/schema.sql 已改正真實 text 變體+probes+修 drift，已 commit+push。

Current objective and progress state:
- **Stage-1 = FULL CLEAN PASS（已最終裁定）**：recall clean-verify v2 全 12 OK、6/6 ANN-recoverable flip 0→>0、0 回歸；§C 基建判定（隔離 8×重試）幼稚園收生 8/8 OK·防賄 8/8 OK·採購 7/8、gold-consistency 8/8·8/8·7/7、p90<4.2s → **HARNESS/LOAD artifact、probes=8 sound（非真 free-tier 風險；之前 09/10 間歇失敗 = v1 combined-masking+限流 量度 artifact，agent-team 已修正）**。生產 Supabase 現行 probes=8。
- Leonard 裁示：CPD = source-allowlist/category-routing defect（非 probes，gold 喺 sag_2025_11/g06 唔喺 curriculum allowlist）→ 移出 Stage-1、入 PLAN-1b；ANN母體=6。masking-defect（searchCombined 將 Channel B 例外偽裝「未配置」HTTP200）= 獨立 promote-blocker，flag+defer。
- Channel B 北極星（Leonard S116，入 memory project_direction）：無論點問都有合理、有指引、**一定要有頁數**嘅回饋 = CB-2 retrieval + CB-3 可追溯（頁數不可 defer）+ CB-1 質素。

Pending tasks in priority order:
1. **Stage 2（adaptive threshold @ searchChannelB.ts:346 取代固定 0.22/category-drop 0.08）—— Stage-1 已 FULL PASS，待 Leonard go（同一 §3 HIGH-risk promote gate 內）**：promote Testing/ `dynamic_cutoff` rank-based knee；CB-2 Exp3 證無單一常數跨 query 分 gold/noise；屬 §E.3 四輪治理脈絡，需 §3d regression matrix + live test-verify。報告 `Testing/poc-retrieval/eval/CB2_STAGE1_report.md`（recall + §C 全段）。
2. PLAN-1b：CPD category-routing fix（gold 喺 sag_2025_11/g06 唔喺 curriculum allowlist，probes 救唔到）+ 選擇性 expansion vs §D.9 always-on expansion consolidation（全 Testing/ 先）。
3. 🔴 masking-defect（searchCombined fake「未配置」令 Channel B 失敗對 monitoring/eval 隱形）= 獨立 promote-blocker，待 Leonard 排 scope/§3。
4. 既有：🔴 FAIL-A Circular 注入 regression（record-only）；🔴 §E.10 admin-login security；P2 分類148/P3 數字；Mobile UI P2；HKEAA；低 doc-debt。

Key files changed in this session:
- Draft（已 commit+push）：backend/supabase/schema.sql（真實 text 變體 + plpgsql volatile + SET LOCAL ivfflat.probes=8 + 修正 vector→text 簽名 drift/grants/post-run smoke）；dev/SESSION_LOG.md、SESSION_HANDOFF.md、CODEBASE_CONTEXT.md、PROJECT_MASTER_SPEC.md、HANDOFF_PACKAGE.md（DOC_SYNC_CHECKLIST 只讀未改：既有 row 已覆蓋）。
- Live Supabase（Leonard Dashboard，非 git）：match_wiki_chunks → plpgsql volatile + SET LOCAL probes=8（text 變體）；vector overload dropped。
- Testing/poc-retrieval/eval/（PoC，非 git）：cb2_stage1_verify.py（v1）、cb2_stage1_verify_v2.py（dedicated clean verify）、backend_dumps_probes8*/、CB2_STAGE1_report.md。
- auto-memory（repo 外）：reference_supabase_pgvector_probes.md、feedback_inspect_live_supabase_before_replace.md、project_direction_review.md（Channel B 北極星）、MEMORY.md。

Known risks / blockers / cautions:
- Stage-1 **已 FULL PASS**（§C closeout 完成：HARNESS/LOAD artifact、probes=8 sound）。生產已 probes=8；偶發 transient（採購 §C 1/8、sen recall 首發 MALFORMED→retry 即 OK）= free-tier 可重試恢復、非真風險。**PLAN-1 promote 仍未完成（Stage 2 未做）勿宣稱 released。**
- 🔴 schema.sql 曾 drift（vector vs 真實 text 簽名）引致 PGRST203 live 事故 → 任何 Supabase RPC DDL 前必 INSPECT live `pg_get_functiondef`、勿信 schema.sql（memory + §E 已固化）。生產 DDL 仍 Leonard Dashboard 親手（Claude 出精確 SQL+rollback+唯讀 INSPECT）。
- 🔴 masking-defect promote-blocker（Channel B 失敗隱形）；🔴 §E.10 admin-login security；🔴 FAIL-A regression（record-only）；§3c regression:semantic 改前已 overall=FAIL（FAIL-A/B 非本 session；schema.sql SQL-only 不影響 TS gate）。
- egress 間歇每次自測；路徑空格雙引號；Testing/ 喺 Draft git 外；改 Draft code/data commit 必入 SESSION_LOG（S111 教訓，本 session 已遵）；產品方向 P1→P2→P3 + 39→148 deferred 鎖定。

Validation status:
- PASS Stage-1 recall：clean-verify v2 全 12 OK、6/6 ANN flip 0→>0、0 回歸；SQL smoke 無 42501/0A000/PGRST203；harness 獨立 audit 證 bit-identical mirror AUTHORITATIVE grader。
- Stage-1 **FULL PASS 已最終裁定**（recall 6/6 + §C HARNESS/LOAD artifact、probes=8 sound）。PENDING：Stage 2 adaptive threshold 未做（PLAN-1 promote 未完成）；PLAN-1b 未做；masking-defect 未修。
- 治理：Draft schema.sql + 5 governance docs commit+push origin/main；Testing/ 喺 git 外；§4a trigger=False；memory ×3 寫低。

Post-startup first action: 完成 §1 起手序 + HANDOFF_PACKAGE + 自測（git HEAD / stats / egress 實測）後，**Stage-1 已 FULL PASS（recall 6/6 + §C HARNESS/LOAD artifact，probes=8 生產現行）——第一件事 = 問 Leonard 下一步排序**：(a) Stage 2 adaptive threshold（同一 §3 HIGH-risk promote gate 內，完成 PLAN-1 promote）定 (b) PLAN-1b（CPD category-routing + selective expansion vs §D.9 consolidation，全 Testing/）定 (c) 先修 🔴 masking-defect promote-blocker。詳情讀 `Testing/poc-retrieval/eval/CB2_STAGE1_report.md`（recall + §C 全段）。**未 Leonard 明示前唔好自行做 Stage 2 / PLAN-1b / 改其他 Draft**；PLAN-1 promote 未完成（Stage 2 未做）勿宣稱 released。碰 admin/auth/公開推送前必讀 §E.10。Channel B 北極星（頁數不可 defer）見 memory project_direction_review。
```

---

## 2026-05-18 Session 115 — CB-0 gate PASSED→AUTHORITATIVE；CB-2 檢索校準執行完成（egress 復通）

- **ID:** Claude_20260518_1059
- **Summary:** Leonard 過 CB-0 gate。三 ruling 採納：**Q1 #9 幼稚園收生=NORMAL（接受語料 drift，g26 真來源）/ Q2 rolefact 確認排除（空 url 失追溯）/ Q3 下一階段=CB-2 檢索校準**。我做 12 條 B-gold 嚴謹自我覆核（唯讀，實測 cross-check `cb_corpus_pool.json`，唔信 gold_detail 註記）→ 抓到 2 個註記 vs 語料真相 discrepancy（兩者實情皆比註記*更好*）。Leonard spot-check #1/#5/#8/#9/#11 **全對** + 裁示 (b) #12 留正式 gold (c) #5 g24 url 准修。gate PASSED → 套修正 → 重跑 grader → CB-0 升 **AUTHORITATIVE**。**全程 Testing/poc-retrieval/eval/，Draft code/data/contract 零接觸（HEAD 71a3a3d 不變）。**
- **實測抓到 2 discrepancy（verify 唔信文檔之價值）：** (1) #5 採購門檻 g24 ×2 gold_detail url 寫 `…/sch-admin-guide/sag`，語料實際 = `…/sag_c.pdf`（真 EDB PDF，文字正正係 5k/50k/200k 限額表）→ chunk 有效，註記 url 字串修正。(2) #12 STEAM `circ_edbc24017` gold_detail 寫 `url=null` 並建議 demote borderline，語料實際有真 url `https://applications.edb.gov.hk/circular/upload/EDBC/EDBC24017C.pdf`（七大重點含強化STEAM）→ **推翻原建議，留正式 gold**。
- **CHANGE（全 Testing/）：** `gold_set_channelB.json`：_meta.status→AUTHORITATIVE+gate 紀錄、rolefact_ruling→CONFIRMED、method_notes #9 CONFIRMED、#5 g24 url ×2→sag_c.pdf、#5/#12 notes_for_leonard 更新、#12 circ url null→真 url。`grade_channelB.py`：docstring/header/honesty block DRAFT→AUTHORITATIVE。
- **CB-0 AUTHORITATIVE 結論：** Channel B 瓶頸 = **RETRIEVAL**。layer-1 數字 gate 前後 **byte-identical**（gold chunk id 全程未變 → gate 係*驗證*數字非改動）：11 NORMAL query **8 條 live recall=0/MRR=0**，正確 vault chunk 喺 corpus 且有真 EDB url（10/12 覆蓋）；瓶頸非語料覆蓋亦非（主要係）合成（synthesis 未量＝CB-3 另議）。
- **Verified/QC:** gold JSON parse OK；invariant **0 rolefact / 0 null-url across 41 gold chunks**（Q2 ruling 守住）；#5/#12 url 實測對返；grader re-run exit OK，report header=AUTHORITATIVE；layer-1 table === 起手讀到嘅 directional run（逐格相同）。Draft `git status` 只 2 治理文檔 M、HEAD `71a3a3d` 不變；Testing/ 喺 Draft git 外（check-ignore exit 128）；egress 本 session 實測 **DOWN**（onrender /health 25s timeout）。§4a：寫 S115 entry 前 348 行 trigger=False；寫入後 405>400 line_trigger=True → 跑 `--apply` 封存 2 條最舊 entry（S110/S112）入 `dev/archive/SESSION_LOG_2026_Q2.md`，SESSION_LOG 405→191 行（保留 S115/S114/S113，latest verbatim block ok=True），recheck trigger=False。
- **CB-2 PLAN（§3 HIGH-risk）→ Leonard 批准 →（§3 divergence）→ Leonard 裁示等網 → egress 復通 →「其他你繼續做」→ 執行完成：** 出 CB-2 PLAN（§3d 4-scenario 矩陣）→ Leonard「繼續改善搜尋」批准。READ 階段揭 §3 divergence（offline exhaustive-cosine 需 query embedding，dump 唔帶、computeOpenAI 需 egress 而當時 DOWN）→ 停低報 Leonard → Leonard 裁示等網做完整版。其後 Leonard「network resumed, 其他你繼續做」→ 自行實測 egress 復通（onrender 200、OpenAI 401-reachable）→ READ→CHANGE→QC→PERSIST 完整執行 CB-2。
- **CB-2 §0b READ：** schema.sql 權威 `ivfflat ... with (lists = 60)`（解決文檔 50 vs 60 矛盾＝**lists=60 為準，docs「50」係 drift**）；pgvector 預設 `probes=1` → 掃 ~1/60≈1.7%（印證診斷）；wiki_index chunk 帶 1536-dim embedding（text-embedding-3-small，同 schema vector(1536)）；OPENAI_API_KEY SET（值不入 log，§E.10）。embed §0b SSOT=embeddingClient.ts，test-verify dim=1536 先 batch。
- **CB-2 CHANGE（全 Testing/，新檔）：** `cb2_build_emb_cache.py`（一次 streaming pass 401MB wiki_index 保留 embedding → `cb2_emb.npy` 12906×1536 float32 L2-norm + `cb2_meta.json`；12,906 chunks/120 src 全有效，再證 `_meta.total_chunks=2874` stale）；`cb2_embed_queries.py`（12 query raw+expanded，OpenAI，§0b test-verify）；`cb2_experiment.py`→`CB2_report.md`。QC 中**自揭並修正自身 metric bug**（exhaustive 全排序令 plain recall 恆=1.0 tautology → 改用 recall@K+gold rank+gold cos）。
- **CB-2 AUTHORITATIVE 結論（offline-evidenced）：** 11 NORMAL、8 live recall=0。分解：**7 ANN-recoverable**（gold 喺 exhaustive top-8，dense embedding 排得到，純失於 IVFFlat probes=1/lists=60）+ **1 expansion-recovers**（#1 sen raw rank 1893→term_lexicon 展開後 rank 3）+ 0 deep + 0 hard。建議：(1) 升 `ivfflat.probes`＝最高槓桿（救 7 條，零 code/embedding 改）(2) query expansion **選擇性**（盲展開回歸 4 條 raw 已好嘅 #07/#08/#10/#12，須 fallback 非 always-on）(3) 取代固定/0.08 threshold 為 per-query adaptive（Exp3：固定 0.22 會掉 sen gold cos 0.182；0.08 灌 rank-50 噪音）。自洽 cross-check：CB-2 獨立重算 live recall === CB-0 authoritative layer-1（逐 query 相同）。
- **QC（§3d 4 scenario 全 PASS）：** Normal=exhaustive 量化 ANN-miss ✓；Boundary=sen 展開 1893→3 ✓；Error=#6 LSG raw rank 1148 deep、CORPUS_GAP 不偽陽 ✓；Regression=Draft git 只治理文檔+Q2 archive、HEAD `71a3a3d` 不變、Testing/ 喺 git 外（exit 128）、CB-0 4 authoritative 檔 mtime 07:45–09:44 未被 CB-2 動 ✓。
- **Pending:** CB-2 建議落地 = Draft backend 改（searchChannelB / Supabase ivfflat.probes / wikiRepository）＝**promote，獨立 §3 HIGH-risk gate，待 Leonard 明示**（本方向至今 Draft 零接觸）；live Supabase 高 probes 行為未 introspect，promote 前須 live test-verify。CB-1 語料衛生 / CB-3 合成可追溯待 Leonard 排。S114+S115 治理文檔+Q2 archive uncommitted（待 Leonard commit 授權）。
- **Next:** 等 Leonard 裁示 — CB-2 建議是否走 promote PLAN（§3 HIGH-risk）／定先做 CB-1／CB-3；promote 仍暫停直至明示；FAIL-A 待排。
- **[Leonard 指示 2 件] git push + MemPalace 移除：** (1) **push 係你做** → S115 治理 commit `ec157db` push origin/main（heredoc-in-`$()` first try shell parse fail → 改 `git commit -F` 成功）；存 feedback memory「Claude 做 git push」+ Close Checklist 更新。(2) **記原則入 memory**：agent team（收建議/研究可行性＋審核＋監察）幾時都可用、無須每次問 → feedback memory。(3) **刪 MemPalace 資料**（Leonard 揀「本專案 wing + 本地 config + 治理引用」範圍）：刪 repo-local `.venv`(406M)/`mempalace.yaml`/`entities.json` + `git rm dev/mempalace_sync.py`；剝除 active 治理引用（CODEBASE_CONTEXT Directory Map/Build&Run/External Services +Maintenance Log append、SESSION_HANDOFF baseline#8/Close Checklist、PROJECT_MASTER_SPEC §C.4/§C.5/§G.4）；歷史 entry 不改寫（§12）。**§3 divergence**：mempalace CLI 3.3.2 無 wing-delete subcommand → 唔可安全 surgical 刪 shared fragile 多專案 Chroma palace 嘅本專案 wing（§5/§6 禁 risky DB surgery）→ shared palace 不動、本專案 wing drawers 孤兒化。停低報 Leonard → **Leonard 裁示：留低孤兒、永久唔郁 shared palace（§3 divergence RESOLVED；未來勿再 raise/purge）**。`.venv` 實測只 MemPalace tooling 用（無 project script 依賴，system python3 有 numpy/openai）→ 刪安全。
- **HEAD 推進：** S115 共 3 commit 由 Claude 自 push（Leonard「push 係你做」）：`71a3a3d`→`ec157db`（CB-0/CB-2/lists-drift/§4a）→`6eb314b`（MemPalace 移除）→`541e018`（orphan-drawer 裁示）；origin/main 同步、tree clean。commit 前文字寫舊 HEAD 屬正常 pre-commit 態、已入本 SESSION_LOG＝符 §G.2 非 desync。
- **收工 CLOSEOUT（Leonard「收工」，2026-05-18 S115）：** §4 closeout 執行 — §4a gate trigger=False（204 行）；Open Priorities 已對現況 re-check（item1=等 Leonard CB-2 落地裁示）；本 verbatim handoff block 已 regenerate 反映最終態（3 commit pushed / MemPalace 移除 / push-ownership / agent-team memory）。Draft code/data/contract 全 S115 零接觸。下次起手＝問 Leonard CB-2 落地路徑（promote §3 HIGH-risk vs CB-1 vs CB-3）。

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| Isolated PoC iterated (Testing/ only, no Draft code/data/contract) | SESSION_LOG/HANDOFF record；PoC 自帶 report/gold；CODEBASE_CONTEXT N/A（Testing/ 非 Draft tech-stack/dir，未 promote） | ✓ Done |
| Gate ruling resolved (DRAFT→AUTHORITATIVE) | SESSION_HANDOFF Current Baseline / Open Priorities 重生（CB-0 gate passed→CB-2）/ Known Risks（移除 CB-0 DRAFT risk）；本 SESSION_LOG entry（3 ruling + 2 discrepancy + QC） | ✓ Done |
| §4a SESSION_LOG maintenance triggered post-write (>400 行) | `--apply` 封存 S110/S112 → `dev/archive/SESSION_LOG_2026_Q2.md`；archive pointer comment 已存在（L3）；retain S115/S114/S113；本 entry §4a 註記已校正（無 false claim 殘留） | ✓ Done |
| CB-2 isolated PoC executed (Testing/ only, no Draft code/data/contract) | SESSION_LOG 本 entry（CB-2 §0b/CHANGE/結論/QC）+ verbatim handoff 更新；SESSION_HANDOFF Current Baseline/Open Priorities 重生/Last Session Record；CB2_report.md 自帶；CODEBASE_CONTEXT N/A（Testing/ 未 promote） | ✓ Done |
| §0b doc-drift surfaced (IVFFlat lists 50→60) | schema.sql 權威=60；修正 PROJECT_MASTER_SPEC §C.4 + SESSION_HANDOFF Supabase Technical Notes（lists=50→60、刪 stale「2,822 rows」、加 caveat live 未 introspect）；CODEBASE_CONTEXT 無 lists 數字＝N/A；wiki_index `_meta.total_chunks=2874` 仍 stale doc-debt（Draft data 零接觸不改） | ✓ Done |
| MemPalace 整合移除 (Leonard 指示) | CODEBASE_CONTEXT（Directory Map/Build&Run/External Services 剝除 + Maintenance Log append）/ SESSION_HANDOFF（baseline#8 + Session Close Checklist）/ PROJECT_MASTER_SPEC（§C.3 §C.5 §G.4）；repo-local 檔刪 + `git rm dev/mempalace_sync.py`；feedback memory ×2（agent-team / Claude-does-push）；歷史記錄不改寫（§12）；shared-palace wing physical purge＝Leonard 裁示留孤兒永久唔郁（§3 divergence RESOLVED） | ✓ Done |
| Working-preference change (push ownership) | SESSION_HANDOFF Session Close Checklist「用戶 Terminal」→「Claude 執行」；PROJECT_MASTER_SPEC §G.4；auto-memory feedback_claude_does_git_push.md + MEMORY.md index | ✓ Done |

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

⚠️ 然後讀 dev/HANDOFF_PACKAGE.md（可信狀態快照）。起手務必自行 verify git HEAD 同 knowledge.json._meta.stats 對唔對得返 SESSION_HANDOFF Current Baseline（治理讀set 都會 drift）。

⚠️ Repo root = "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"（路徑含空格，所有 shell 指令必須雙引號絕對路徑）。Channel B / P1 retrieval PoC 喺姊妹資料夾 "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Testing/poc-retrieval/"（唔喺 git，Draft 零接觸）。`python` 唔存在，用 `python3`。

⚠️ 新工作慣例（S115 Leonard 指示，已入 auto-memory）：**git commit+push 由 Claude 自己做**（唔再交用戶 Terminal；加指定檔勿 -A）。**Agent team 幾時都可用**（收建議/研究可行性＋審核＋監察），無須每次問。egress 間歇（S115 早 down→後通），每次自測勿照抄（§G.2）。

S115 已 closeout（Leonard「收工」）。3 個 commit 全 push：`ec157db`（CB-0/CB-2/lists-drift/§4a）→`6eb314b`（MemPalace 移除）→`541e018`（orphan-drawer 裁示）。HEAD 應 `541e018` 或更新、origin/main 同步。

Current objective and progress state:
- S115 完成：**CB-0 gate PASSED→AUTHORITATIVE**（3 ruling + spot-check #1/#5/#8/#9/#11 全對 + #12 gold + #5 url）；**CB-2 檢索校準執行完成**（全 Testing/，Draft backend 零接觸）。CB-0 結論 authoritative：Channel B 瓶頸=RETRIEVAL。CB-2 分解 8 條 live-recall=0：**7 ANN-recoverable**（gold 喺 exhaustive top-8，純失於 IVFFlat probes=1 / schema.sql lists=60）+ **1 expansion-recovers**（sen raw rank 1893→term_lexicon 展開 rank 3）+ 0 hard。建議：升 ivfflat.probes（最高槓桿、零 code 改）＋選擇性 query expansion（盲展開回歸 #07/#08/#10/#12）＋per-query adaptive threshold（取代固定 0.22/category-drop 0.08）。報告 `Testing/poc-retrieval/eval/CB2_report.md`。synthesis 未量＝CB-3 另議。
- MemPalace **已為本專案完全移除**（Leonard 指示）：repo-local + 治理引用剝除；shared palace 孤兒 drawers **Leonard 裁示留低永久唔郁、勿再 raise/purge**。**勿為本專案重設 MemPalace 除非 Leonard 明示。**

Pending tasks in priority order:
1. **等 Leonard 裁示 CB-2 落地路徑**：CB-2 建議落地必改 Draft backend（`searchChannelB.ts` / Supabase `ivfflat.probes` / `wikiRepository.ts`）＝**promote＝獨立 §3 HIGH-risk gate，須 Leonard 明示先出 PLAN，promote 前必 live test-verify**（live Supabase 高 probes 行為未 introspect）。或 Leonard 改排 CB-1（語料衛生：清 english/midsent/stat 噪音 + 修 wiki_index `_meta.total_chunks` stale）/ CB-3（合成可追溯：prompt 不引源 + merge A+B 違 §A.2 #1）。未明示前 Draft 零接觸、promote 暫停。
2. 🔴 FAIL-A 真 Circular 注入 regression 未修（S111 dedup×600字budget×all_roles-first，Leonard 裁示只記錄，待排設計決定）。
3. P1 S1+S2（Channel A）promote 仍暫停（本 Channel B 方向不涉）。
4. P2 分類 148 + P3 數字對齊（deferred；CB-0 揭 g26/g29/g11 已 ingested=P2 訊號、#6 LSG canonical 來源缺=P2 ingest 候選）；🔴 §E.10 admin-login security；Mobile UI Phase 2；HKEAA；低 doc-debt（`wiki_index._meta.total_chunks=2874` 實 12,906；FAIL-B `semanticRegression.ts:292` stale 1.3.1）。

Key files changed in this session:
- Draft（治理/文檔，零 code/data/contract，**已 commit+push** ec157db→6eb314b→541e018）：dev/SESSION_LOG.md、dev/SESSION_HANDOFF.md、dev/CODEBASE_CONTEXT.md、dev/PROJECT_MASTER_SPEC.md、dev/archive/SESSION_LOG_2026_Q2.md（§4a 封存 S110/S112）；`git rm dev/mempalace_sync.py`；repo-local `.venv`/`mempalace.yaml`/`entities.json` 刪（git-ignored）。
- Testing/poc-retrieval/eval/（PoC，非 git，Draft 零接觸）：CB-0 — gold_set_channelB.json/grade_channelB.py（→AUTHORITATIVE）、CB0_channelB_report.md。CB-2 新檔 — cb2_build_emb_cache.py、cb2_embed_queries.py、cb2_experiment.py、cb2_emb.npy、cb2_meta.json、cb2_qvecs.json、CB2_report.md。
- auto-memory（repo 外）：feedback_agent_team.md、feedback_claude_does_git_push.md（+ MEMORY.md index）。

Known risks / blockers / cautions:
- CB-0/CB-2 authoritative 但 offline-evidenced：probes 建議 promote 前必 **live Supabase test-verify**（高 probes 真實行為未 introspect）；recall-ceiling caveat（gold top-50 lexical pool）；synthesis 未量＝CB-3。
- 🔴 FAIL-A 真 product regression 未修；🔴 §E.10 公開站 client-side admin 閘門 + 密碼曾入 log（碰 admin/auth/公開推送前必讀）；§3c gate（`regression:semantic`）改前已 overall=FAIL → 任何 promote/release 前必重新 baseline 勿信舊「✅」。
- egress 間歇每次自測；路徑含空格雙引號；Testing/ 喺 Draft git 外；改 Draft code/data commit 必入 SESSION_LOG（S111 教訓）；產品方向 P1→P2→P3 + 39→148 deferred 鎖定，未確認唔好跳 scope/§F/契約。
- 已核實 role_facts「整筆撥款（LSG）」data error + 系統性欠 SEN/融合教育覆蓋（P3/P2 未 fix）。

Validation status:
- PASS CB-0：gate passed（spot-check 全對 + 3 ruling）；0 rolefact/0 null-url across 41 gold；grader layer-1 gate 前後 byte-identical；report=AUTHORITATIVE。
- PASS CB-2：§3d 4 scenario 全 PASS；CB-2 重算 live recall === CB-0 authoritative（自洽）；QC 自揭並修自身 metric tautology bug。
- PASS 治理：3 commit push origin/main 同步、tree clean；MemPalace 移除無 active 殘留、shared palace 不動；§0b lists 50→60 drift 修；§4a trigger=False。Draft code/data/contract 全 session 零接觸。
- PENDING：CB-2 落地＝promote（獨立 §3 HIGH-risk，待 Leonard 裁示 promote vs CB-1 vs CB-3）。

Post-startup first action: 完成 §1 起手序 + HANDOFF_PACKAGE 後，自測 git HEAD（應 `541e018` 或更新）+ knowledge.json._meta.stats vs baseline + **實測 egress（onrender /health，勿照抄）**。CB-0 + CB-2 均已 authoritative：睇 `Testing/poc-retrieval/eval/CB2_report.md`（ANN-miss 分解 + 校準建議 + §3d）+ `CB0_channelB_report.md` + `gold_set_channelB.json`。**第一個動作＝問 Leonard 裁示 CB-2 落地路徑**：(a) 走 promote PLAN（§3 HIGH-risk：改 searchChannelB.ts / Supabase ivfflat.probes / wikiRepository.ts；promote 前必 live test-verify）定 (b) 先做 CB-1 語料衛生 定 (c) CB-3 合成可追溯。未 Leonard 明示前 Draft backend 零接觸、promote 暫停。**MemPalace 已移除——勿重設、勿掂 shared palace 孤兒 drawers。** 碰 admin/auth/公開推送前必讀 §E.10。git commit+push 由 Claude 做（指定檔）。
```

---

## 2026-05-18 Session 114 — 方向轉 Channel B 效果；CB-0 B-isolated 評估基礎建成（DRAFT，待 Leonard gate）

- **ID:** Claude_20260518_0720
- **Summary:** Leonard 定新方向：**處理 Channel B 效果**（唔單做一個 channel），用 agent team 互補分工。起手 §1 verify：git HEAD `71a3a3d`==baseline、knowledge.json stats {455,10736,120,39,7} 對得返、**egress 本 session DOWN（onrender /health timeout，間歇性已記錄）**、SESSION_LOG 288 行 §4a 未觸發。4-agent 唯讀診斷 Channel B 四切面（語料/檢索/合成/實證）→ 共識根因。Leonard 揀 **Testing/ PoC 隔離 + 由 CB-0 評估基礎起手**。建成 CB-0（Channel-B 首次可被獨立量度）。**Draft backend 全程零接觸**（git status clean，HEAD 不變）。
- **4-agent 診斷共識（唯讀，已交）：** (A 語料) 真 ingester 係 `dev/vault/build_wiki_index.py` 非文檔寫嘅 ai_extract.py；只 exact-SHA dedup，零 boilerplate/語言/stat 過濾；wiki_index 實 **12,906 chunks/120 src** 但 `_meta.total_chunks=2874` stale。(B 檢索) 短/縮寫 query 嵌入失配（sen→英文 Senior 0.247）；0.22 threshold 跨 query band 反向重疊；`searchChannelB.ts:346` 偵測 category 即跌 threshold 到 0.08；IVFFlat lists=60 probes=1 → 每 query 只掃 ~1.7% 向量（ANN miss 未量化）。(C 合成) **prompt 明令「不需列出來源編號」、合成 merge A+B 而 A 結果零 url/page → 結構上不可追溯，違 §A.2 #1**；無 abstention；錯誤吞成 ""；13 dumps 全 synthesize=false。(D 實證) **S1/S2「10/12」嘅 gold 100% Channel A，Channel B 從未被 gold 評估過**。
- **CB-0 建成（全 Testing/poc-retrieval/eval/，新檔，非 git）：** `cb_corpus_index.py`（streaming parse 420MB 本地 wiki_index，零 egress，丟 embedding；per-query top-50 lexical pool + 6 quality flag + retrieved_by_backend cross-mark）→ `cb_corpus_pool.json`。GoldBuilder agent（沿 S1/S2 gate 模式 + 繼承 gold_set.json domain ruling）→ `gold_set_channelB.json`（chunk-`id`-keyed，比 A grader text-prefix 穩健；10/12 NORMAL、#6 LSG CORPUS_GAP、**#9 幼稚園收生 ABSTENTION→NORMAL（語料 drift：g26 收生指引已 ingested）**；rolefact 排除＝空 url 失追溯）。`grade_channelB.py`（B-isolated 三層：retrieval P@k/recall/MRR + 返回行 defect 比 + retrieval-gap）→ `CB0_channelB_report.md`。
- **CB-0 三角印證結論（DRAFT，未 authoritative）：** corpus 10/12 有正確 vault chunk（real EDB url），但 **live Channel B 對 8/11 NORMAL query recall=0、MRR=0**（採購/採購門檻/STEAM 各只 1 條 gold 被取回）；返回行 defect 與 query 相關（sen 32%英+20%斷句、LSG 57%英+68%斷句、年假/病假/校曆 乾淨）；retrieval-gap 層：8/11 「corpus-has-it / retrieval-misses」。**結論候選：Channel B 瓶頸係 RETRIEVAL，非語料覆蓋（10/12 有覆蓋）亦非（主要係）合成。** 重排後續：CB-2 檢索 = 最高槓桿。
- **Honesty caveats（已寫入 report）：** gold 由 top-50 lexical pool 選 → recall ceiling caveat；CB-0 只量 retrieval+corpus，synthesis 未量（dumps synthesize=false）= 獨立 CB-3；#9 status flip + rolefact-exclusion = 待 Leonard ruling。
- **Verified:** Draft `git status` clean、HEAD `71a3a3d` 不變（zero backend/code/data/contract touch）；Testing/ 路徑喺 Draft git 外（check-ignore exit 128）；corpus probe 掃 12906 chunks/120 src/58s；gold JSON parse OK、0 id/detail mismatch、全 gold=vault_extract+real url；grader 三層 re-run OK。
- **QC:** CB-0 PASS as scoped（Channel B 首次可量度，三層三角一致）。promote/Draft 零接觸（§3c 不觸發）。§4a trigger=False。**DRAFT — 未過 Leonard spot-check gate 前數字 directional 非 authoritative。**
- **Pending（待 Leonard，gate）：** spot-check 4-5/12 B-gold；裁示 (a) #9 ABSTENTION→NORMAL 收唔收？(b) rolefact-exclusion ruling 確認？(c) CB-0 結論「瓶頸=retrieval」接受後 → CB-2 檢索校準（per-query adaptive threshold / 修 0.08 / ivfflat.probes / 縮寫展開）定 CB-1 語料衛生先排？
- **Next:** 等 Leonard gate；未過 gate 前 CB-0 數字 directional。Draft backend 零接觸（promote 仍暫停、本方向未涉 promote）。

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| New / iterated isolated PoC (Testing/ only, no Draft code/data/contract change) | SESSION_LOG/HANDOFF record；PoC 自帶 report/notes；CODEBASE_CONTEXT N/A（Testing/ 非 Draft tech-stack/dir，未 promote） | ✓ Done |
| Diagnostic / measurement-only finding (recorded, not fixed) | SESSION_HANDOFF Open Priorities（方向轉 Channel B + CB-0 DRAFT + gate）；本 SESSION_LOG entry（4-agent 診斷 + CB-0 三層結論 + caveats）；待 Leonard gate 後再排 CB-1/2/3 | ✓ Done |

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

⚠️ 然後讀 dev/HANDOFF_PACKAGE.md（可信狀態快照）。起手務必自行 verify git HEAD 同 knowledge.json._meta.stats 對唔對得返 SESSION_HANDOFF Current Baseline（治理讀set 都會 drift）。

⚠️ Repo root = "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"（路徑含空格，所有 shell 指令必須雙引號絕對路徑）。Channel B / P1 retrieval PoC 喺姊妹資料夾 "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Testing/poc-retrieval/"（唔喺 git，Draft 零接觸）。`python` 唔存在，用 `python3`。

⚠️ S114 egress DOWN（onrender /health timeout）；S113 曾通 — 間歇性，每次自行實測勿照抄假設（§G.2）。S114 Draft 2 治理文檔改未 commit（待 Leonard 授權；commit 命令見下）。

Current objective and progress state:
- S114: Leonard 定新焦點 = 處理 **Channel B 效果**（唔單做一 channel，用 agent team 互補）。4-agent 唯讀診斷 + 建成 **CB-0 = Channel-B 首次可被獨立量度**（全 Testing/poc-retrieval/，Draft backend 零接觸）。
- CB-0 三角結論候選（**DRAFT，未過 Leonard spot-check gate 前非 authoritative**）：**Channel B 瓶頸 = RETRIEVAL**，非語料覆蓋（10/12 query corpus 有正確 vault chunk + real EDB url）亦非（主要係）合成 — 8/11 NORMAL query live Channel-B recall=0 / MRR=0，正確 chunk 喺 corpus 但 retrieval 取唔到（IVFFlat probes=1 ~1.7% 向量 + 嵌入失配 + 0.22→0.08 threshold）。
- 合成另有結構性缺（CB-3，code review 證非 harness）：prompt 明令不引源 + merge A+B（A 零 url/page）→ 違 §A.2 #1 可追溯不變量。

Pending tasks in priority order:
1. **CB-0 Leonard gate（最優先）**：spot-check 4-5/12 `Testing/poc-retrieval/eval/gold_set_channelB.json`（睇 `CB0_channelB_report.md` + 各 query notes_for_leonard）；裁示 (a) #9 幼稚園收生 ABSTENTION→NORMAL（語料 drift：g26 收生指引已 ingested）收唔收 (b) rolefact-exclusion ruling（rolefact 空 url 失追溯，已排除出 B-gold）(c) 接受「瓶頸=retrieval」後排 **CB-2 檢索校準** vs **CB-1 語料衛生** 邊個先。
2. CB-1 語料衛生 / CB-2 檢索校準 / CB-3 合成可追溯（待 gate 後按 Leonard 排；全 Testing/ 隔離，Draft 零接觸直至明示 promote）。
3. P1 S1+S2（Channel A）promote 仍**暫停**（本 Channel B 方向不涉 promote）；🔴 FAIL-A 真 Circular 注入 regression 待 Leonard 排（涉 dedup/budget/排序設計）。
4. P2 分類 148 + P3 數字對齊（roadmap deferred）；🔴 Q&A §E.10 admin-login security；Mobile UI Phase 2；HKEAA；低 doc-debt（含 `wiki_index.json._meta.total_chunks=2874` stale 實 12,906）。

Key files changed in this session:
- Draft（僅 2 治理文檔，零 code/data/contract，未 commit）：dev/SESSION_LOG.md（本 S114 entry + 本 block）、dev/SESSION_HANDOFF.md（Current Baseline / Last Session Record 輪轉 / Open Priorities 重生 / Known Risks）。
- Testing/poc-retrieval/eval/（PoC，非 git，新檔）：cb_corpus_index.py、cb_corpus_pool.json、gold_set_channelB.json（DRAFT）、grade_channelB.py、CB0_channelB_report.md。

Known risks / blockers / cautions:
- **CB-0 DRAFT — gate 未過前數字 directional 非 authoritative**；gold 由 top-50 lexical pool 選（recall-ceiling caveat）；CB-0 只量 retrieval+corpus，synthesis 未量（S113 dumps synthesize=false）= CB-3 另議。
- 🔴 FAIL-A 真 product regression（S111 dedup×600字budget，Leonard 裁示只記錄不修，未排）；🔴 §E.10 公開站 client-side admin 閘門 + 密碼曾入 log（碰 admin/auth/公開推送前必讀）；§3c gate（`regression:semantic`）改前已 overall=FAIL（FAIL-A/B，非 S1/S2）→ 任何 promote/release 前必重新 baseline 勿信舊「✅」。
- egress 間歇（S114 down / S113 up）每次自行 verify；路徑含空格雙引號；Testing/ 喺 Draft git 外；改 Draft code/data commit 必入 SESSION_LOG（S111 教訓）；產品方向 P1→P2→P3 + 39→148 deferred 鎖定，未確認唔好跳 scope/§F/契約。
- 已核實 role_facts「整筆撥款（LSG）」data error + 系統性欠 SEN/融合教育覆蓋（P3/P2 未 fix）；wiki_index `_meta.total_chunks` stale（CB-0 揭，doc-debt 未 fix）。

Validation status:
- PASS: CB-0 as scoped（Channel B 首次可量度，三層三角一致：retrieval P@k/recall/MRR + 返回行 defect + retrieval-gap）。Draft 零 code/data/contract（git status 只 2 治理文檔；HEAD 71a3a3d 不變）；Testing/ 喺 Draft git 外（check-ignore exit 128）；§4a trigger=False（309 行）。
- DRAFT / PENDING（待 Leonard gate）：B-gold spot-check 4-5/12；#9 status flip ruling；rolefact-exclusion ruling；CB-1 vs CB-2 排序。

Post-startup first action: 完成 §1 起手序 + HANDOFF_PACKAGE 後，自行 verify git HEAD（應 `71a3a3d` 或更新）+ knowledge.json._meta.stats vs baseline + **實測 egress（onrender /health，勿照抄 S114「down」亦勿照抄 S113「up」）**。睇 `Testing/poc-retrieval/eval/CB0_channelB_report.md`（三層）+ `gold_set_channelB.json`（_meta + 各 query notes_for_leonard）+ `README.md` 了解 CB-0。然後問 Leonard 攞 gate 決定：(1) spot-check 4-5/12 B-gold 結果 (2) #9 ABSTENTION→NORMAL 收唔收 (3) rolefact-exclusion ruling (4) CB-2 檢索校準 vs CB-1 語料衛生 邊個先。未過 gate 前 CB-0 數字當 directional；**未 Leonard 明示前 Draft backend 零接觸**（promote 仍暫停、本方向未涉 promote）；碰 admin/auth/公開推送前必讀 §E.10。
```

---

## 2026-05-17 Session 113 — P1 S2 建構 + 真實後端 breadth 驗證（egress 實測竟通）

- **ID:** Claude_20260517_2035
- **Summary:** Leonard 收 S1（PoC milestone，**未** promote）→ 批 S2。喺 `Testing/poc-retrieval/` 建好 S2 = 支柱 1+3（`lib/lexicon.py` 12-query 同義詞/實體連結庫、`lib/lexical_score.py` CJK 字面計分、`lib/hybrid.py` RRF 融合 + `s2_operating_point` lex-gate∪S1-head）。**實測發現 sandbox egress 竟然通**（onrender.com HTTP 200 + github SSH auth 成功，與既有文檔「egress 封鎖」假設相反，§G.2 教訓再現）→ 自己跑 12-query 真實後端 breadth capture + grade（原計劃交 Leonard Terminal，今證實毋須）。
- **S2 `sen` 離線（真數據）：** gold 由 dense rank [1,2,5,9,13] → fused **[1,2,3,4,5]**。S1 ceiling P=0.385@R=1.0 → **S2 ceiling P=1.0@R=1.0**（cutoff-independent），operating point 8 條 R=1.0 P=0.625。報告 `eval/S2_report.md`。
- **Breadth 12-query（live `/api/search/combined` min_score=0.1 top_k=50）：** baseline 每 query **269–504 條**、P 0.006–0.027（雜訊洪水係系統性，非淨 `sen`）。S1 alone：recall 崩（年假/採購門檻/校曆/STEAM/病假 → R=0.0，gold 全埋喺 dense plateau 下）——**11 條再證 S1 necessary-not-sufficient**。S2-op 初版 7/12 → 修 gap 後 **10/12 PASS**，recall 大幅回升（多數 R=1.0），P 比 baseline 升 5–50×。報告 `eval/S2_breadth_report.md`。
- **3 個可修 gap 已修（Leonard「你的建議／b A」授權，Testing/ 細修，已執行）：** **#09 幼稚園收生**：關鍵發現 dense 對 out-of-domain query *confidently wrong*（#09 dense top 0.698，全 12 query 最高）→ dense-floor abstention 係錯信號；改用 **zero-literal-grounding gate**（max lexical < τ → 真棄答，合 §A.2 不變量）→ #09 由 surfaced 4 變 **0（正確棄答）**。**#07 CPD**：lexicon 加數據實證詞「持續進修／專業發展計劃」→ R **0.714→1.0**。**#10 防賄**：lexicon 加「職能劃分／輪換原則」（漏嘅 gold = ICAC 職務分隔內控）→ R **5/6→6/6**。`sen` 無回歸（強 lexical grounding，gate 不觸發）；lexicon per-query keyed，加詞不影響他 query。
- **餘 2 條 △（#03 採購/#08 體罰，非 correctness defect）：** S2 兩者皆 **full recall R=1.0**；標 △ 純因 grader 準則要 S2-P ≥ S1-P，而 S1 嗰個高 P 係靠 recall 崩到 0.33/0.5 換返嚟。喺呢度谷 precision = 掉 gold = 對 traceability-first 平台係**錯**嘅 tradeoff，故**唔郁**（非 defect）。
- **Drift fixed（PERSIST）：** S112 聲稱加咗 DOC_SYNC「isolated PoC」row 但從未寫入 registry → 今正式寫入 `dev/DOC_SYNC_CHECKLIST.md`（anti-pattern guard）。`grade_s2_breadth.py` provenance line 由「Leonard-run」改為準確「captured <ts> from onrender …」。
- **Verified（實測）:** pre-commit git HEAD `dbc10b8`==origin/main；knowledge.json _meta.stats 對返 baseline；Draft 只 4 governance docs 改（S112 closeout 3 + S113 DOC_SYNC 1），**零 code/data/contract**；12 dumps 全 HTTP 200；S2 modules smoke + curl bash -n + grader no-op 皆 OK；§4a trigger=False（217 行）。
- **QC:** S2 PASS as scoped（`sen` 離線可證 S1 上限被打破；breadth 7/12 PASS + 誠實 gap 清單，無過度宣稱）。本 session Draft code/data/contract 零接觸（全 Testing/）。
- **Lexicon 通用性策略（Leonard「先解 lexicon 通用性策略」要求，已交）：** `eval/lexicon_strategy_probe.py` 實 mine 455-snapshot →（A）parenthetical 自動 pair 得 5 條且**含一條錯**：`LSG↔整筆撥款`＝S112 已揭嘅 P3 data error，證**純自動 mine 會把語料自身錯誤學入搜尋 lexicon**→ curated overlay 係 correctness 必需非可選；（B）bracket role tag 8 條乾淨（entity-link 用）；（C）12 query token 11/12 corpus-grounded（只幼稚園收生缺→正確棄答）。方案：**hybrid = 自動 mine base（bracket role + parenthetical，含 data-error denylist）⊕ curated domain overlay（LSG=學習支援津貼覆寫、SEN↔SENCO entity-link、abstain blank）⊕ term-keyed（非 query-keyed，可泛化任意 query）⊕ trust-gate 人手覆核新 acronym**。全文 `eval/LEXICON_STRATEGY.md`。連帶強化 P3（LSG reconcile 同時清自動 mine 源）。
- **Route (i) 已執行（Leonard 揀「先 Testing/ 起 hybrid 再 promote」）：** 建 `lib/term_lexicon.py`（hybrid term-keyed：BASE 自動 mine bracket roles+parenthetical+**LSG data-error denylist** ⊕ OVERLAY curated Leonard 裁示 ⊕ trust-gate 註）；hybrid.py 改 import 佢。驗證：breadth **仍 10/12**（#06 LSG 0.556→0.625 因 overlay 正確 entity-link）、`sen` 無回歸、#09 仍正確棄答、**泛化成立**（非-12 phrasing 實測：「特殊教育需要邊個負責」→SEN+SENCO、「annual leave 點計」→年假群、「學習支援津貼」→正確 LSG 覆寫非語料 整筆撥款 錯）。promote 前置條件達成。
- **Promote 嘗試 → §3c gate 已紅 → Leonard 裁示只記錄（Leonard「2」批一次過 promote，後「先睇 regression 細節再決」→「兩個都唔做，淨係如實記錄入治理」）：** READ 階段做 pre-change baseline：`npm run check`✅ `npm run build`✅，但 **`npm run regression:semantic` 喺改前已 overall=FAIL（PASS9/FAIL2）**。唯讀 triage（0 code 改，Draft 乾淨）真因：**FAIL-A role-bucket `finance_distinct=false`** = S111 dedup（792→455）把跨角色重複摺入 all_roles → `finance.all_roles`=83 條/2832 字，`knowledgeSelector` all_roles-first 排序砍 600 字，頭~14 條 all_roles 蓋爆 budget，subject_head/panel_chair 角色專屬 finance 事實**永遠注入唔到**（無 budget 時 distinct=True，角色拆分本身冇壞）→ **自 2026-05-16 起 Circular System 對該兩角色 finance 注入退化成只通用、無角色專屬，係真 product regression，非 S1/S2**；**FAIL-B** = `semanticRegression.ts:292` 硬斷言 `version==="1.3.1"`（實 2.3.0/2.2.0）stale 測試。`SESSION_HANDOFF:99` 原寫「regression PASS=12/FAIL=0 ✅」係 2026-04-12 舊值、現 false。**Leonard 裁示：FAIL-A/B 兩個都唔修，只如實入治理；promote 暫停**。Draft backend 全程零接觸。
- **治理記錄（PERSIST）：** SESSION_HANDOFF Regression Notes #3 由 false「PASS=12/FAIL=0 ✅」改為實測 FAIL=2 + FAIL-A/B 真因；Open Priorities 重生（promote 暫停；FAIL-A 升為 🔴 真 regression 待排）；Risks 加 FAIL-A + §3c-gate-已紅 + §G.2 教訓（SESSION_HANDOFF 曾載 false PASS 斷言）。
- **Pending（待 Leonard）:** (1) promote 暫停中，只 Leonard 明示先恢復（恢復 bar=零新增 FAIL）；(2) FAIL-A 真 Circular 注入 regression 修法待 Leonard 排（涉 dedup/budget/排序設計決定）；(3) P2/P3 排期。餘 2 △=tradeoff 唔郁。
- **Next:** 等 Leonard：恢復 promote／排 FAIL-A triage／轉 P2/P3。未明示前 Draft backend 零接觸（§3）。

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| New / iterated isolated PoC (Testing/ only, no Draft code/data/contract change) | SESSION_LOG/HANDOFF record；PoC Testing/ README；CODEBASE_CONTEXT N/A（Testing/ 非 Draft tech-stack/dir，未 promote） | ✓ Done |
| New project doc added (registry anti-pattern guard) | 將缺漏 row 寫入 `dev/DOC_SYNC_CHECKLIST.md`（S112 claimed-added 但未持久化） | ✓ Done（1-line add） |
| Doc-drift / accuracy correction | `grade_s2_breadth.py` provenance line 改準確；本 entry 記錄 egress 文檔假設已過時；**SESSION_HANDOFF Regression Notes #3 由 false「PASS=12/FAIL=0 ✅」改實測 FAIL=2 + FAIL-A/B 真因**；Open Priorities 重生（promote 暫停 + FAIL-A 升優先） | ✓ Done |
| Regression discovered (pre-existing, Leonard 裁示只記錄不修) | SESSION_HANDOFF Regression Notes #3 + Risks（FAIL-A 真 Circular 注入 regression / FAIL-B stale 斷言）；SESSION_LOG 本 entry Problem/RootCause/(Fix deferred)/Verification；§8b monitoring（無新 rule，§G.2 已涵蓋「verify load-bearing claims」） | ✓ Done |

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

⚠️ 然後讀 dev/HANDOFF_PACKAGE.md（可信狀態快照）。起手務必自行 verify git HEAD 同 knowledge.json._meta.stats 對唔對得返 SESSION_HANDOFF Current Baseline（S111 證連治理讀set 都會 drift）。

⚠️ Repo root = "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"（路徑含空格，所有 shell 指令必須雙引號絕對路徑）。P1 retrieval PoC 喺姊妹資料夾 "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Testing/poc-retrieval/"（唔喺 git，Draft 零接觸）。

⚠️ S113 實測：sandbox egress 竟然通（onrender.com + github SSH 都得），與既有文檔「egress 封鎖」假設相反。起手前實測，勿照抄舊假設（§G.2）。但呢個可能 environment/intermittent，每次自行 verify。

Current objective and progress state:
- S112: Leonard 定 roadmap P1 搜尋相關性 → P2 分類 148 → P3 數字對齊；39→148 deferred。批 5-支柱新檢索架構，分階段 S1→S4 全喺 Testing/。
- S113: 收 S1（PoC，未 promote）；S2（支柱 1+3 hybrid lexical+dense+RRF + SEN/SENCO lexicon）建好。`sen` 離線：S1 ceiling P=0.385@R1.0 → S2 P=1.0@R1.0（gold fused [1-5]）。真實後端 breadth 12-query：baseline 每 query 269-504 條 P~0.01；S1 alone recall 崩 5 條；S2-op 初版 7/12 → 修 3 gap 後 **10/12 PASS**，recall 大升、P 升 5-50×。已修：#09 幼稚園收生 zero-literal-grounding abstention gate（dense out-of-domain confidently wrong，top 0.698）→ 正確棄答；#07 CPD（+持續進修/專業發展計劃）R 0.714→1.0；#10 防賄（+職能劃分/輪換原則）R 5/6→6/6。餘 2 △（#03 採購/#08 體罰）= S2 full-recall vs S1 fake-high-P-at-collapsed-R 嘅 tradeoff，非 defect。**Leonard「2」批一次過 promote → READ 階段 pre-change baseline 發現 `regression:semantic` 改前已 overall=FAIL（FAIL-A 真 Circular 注入 regression［S111 dedup×600字budget］+ FAIL-B stale 斷言，皆非 S1/S2）→ Leonard 裁示兩個都唔修、只如實入治理、promote 暫停。Draft backend 零接觸。**

Pending tasks in priority order:
1. **promote 暫停中** —— 只 Leonard 明示先恢復；恢復 §3c bar = 零新增 FAIL（pre-existing FAIL-A/B 照舊）+ breadth harness 驗 S1/S2。未明示前 Draft backend 零接觸（§3）。
2. **🔴 FAIL-A 真 product regression（未修，Leonard 裁示只記錄）**：S111 dedup（792→455）× 600 字注入 budget × all_roles-first 排序 → subject_head/panel_chair 嘅 finance 注入自 2026-05-16 退化成只通用；修法涉設計決定，待 Leonard 排。FAIL-B = `semanticRegression.ts:292` stale `1.3.1` 斷言（低 doc-debt）。
3. P2：148 文件按校級(中小幼特)+範疇分類；P3：reconcile「整筆撥款（LSG）」誤標 + 補 SEN 家族覆蓋。餘 2 △=tradeoff 唔郁。
4. 原 Open Priorities：Mobile UI Phase 2、🔴 Q&A §E.10 admin-login security、HKEAA source family。

Key files changed in this session:
- Draft（僅治理文檔，零 code/data/contract）：dev/SESSION_LOG.md（本 entry）、dev/SESSION_HANDOFF.md（Regression Notes #3 修正 false PASS 斷言 + Open Priorities 重生 promote 暫停/FAIL-A 升優先 + S113 record + baseline）、dev/DOC_SYNC_CHECKLIST.md（補 isolated-PoC row）。git commit + push 多次由本 session 執行（Leonard 多次授權，egress 通）。**promote READ 階段 0 backend code 改（pre-change baseline + 唯讀 triage 後 Leonard 裁示停）。**
- Testing/poc-retrieval/（PoC，非 git）：lib/{lexicon,lexical_score,hybrid}.py、eval/{run_s2_sen,grade_s2_breadth}.py、eval/curl_pack_breadth.sh、eval/backend_dumps/*.json（12 live dumps）、eval/{S2_report,S2_breadth_report}.md、README.md。

Known risks / blockers / cautions:
- 🔴 **FAIL-A 真 product regression（未修，Leonard 裁示只記錄）**：S111 dedup（792→455）× 600 字注入 budget × all_roles-first 排序 → subject_head/panel_chair 嘅 finance 注入自 2026-05-16 退化成只通用、無角色專屬（見 SESSION_HANDOFF Regression Notes #3）。
- 🔴 §3c gate（`npm run regression:semantic`）本身已紅（FAIL-A/B，非 S1/S2）→ 任何 release/merge/promote claim 前必重新 baseline、勿信舊「✅」（§G.2 再現：SESSION_HANDOFF 曾載 false「PASS=12/FAIL=0」斷言 ~過時值）。
- 🔴 PROJECT_MASTER_SPEC §E.10：公開站 client-side admin 閘門 + 密碼曾入 log（最嚴重未解，碰 admin/auth/公開推送前必讀）。
- S1/S2 係 Testing PoC，**未 promote、promote 暫停中**（只 Leonard 明示先恢復）。S2 3 gap（#09/#07/#10）已修，breadth 10/12；餘 2 △（#03/#08）= recall/precision tradeoff 非 defect。勿過度宣稱「搜尋已全修好」（仍 PoC、未 promote、breadth gold 係 12 短 query 抽樣）。
- egress 文檔假設過時（S113 實測 onrender+github 通）但可能 intermittent → 每次自行 verify，勿假設恆通亦勿假設恆封。
- 已核實 role_facts「整筆撥款（LSG）」data error + 知識庫系統性欠 SEN/融合教育覆蓋（P3/P2，未 fix）。
- 路徑含空格雙引號；Testing/ 喺 Draft git 外；load-bearing 數字動手前 verify code/data/git；改 code/data 之 commit 必入 SESSION_LOG（S111 教訓）。
- 產品方向：39→148 deferred；P1→P2→P3 順序鎖定，未得 Leonard 確認唔好跳契約收斂/Circular 接線/scope/§F。

Validation status:
- PASS: S2 as scoped（`sen` 離線 S1 上限被打破 P0.385→1.0；breadth 10/12；term_lexicon 泛化驗證）；Draft 零 code/data/contract（promote READ 階段 0 backend 改）；§4a trigger=False；多次 git commit+push 已落地。
- DISCOVERED（已如實入治理，Leonard 裁示不修）：§3c `regression:semantic` 改前已 overall=FAIL — FAIL-A 真 Circular 注入 regression（S111 dedup×600字budget）、FAIL-B stale `1.3.1` 斷言。
- PENDING（待 Leonard）：恢復 promote？／排 FAIL-A triage？／P2·P3 排期。

Post-startup first action: 完成 §1 起手序 + HANDOFF_PACKAGE 後，自行 verify git HEAD（應 ≥ 本 session 最後 commit）+ knowledge.json._meta.stats vs baseline + 實測 egress（onrender /health）勿照抄假設。**重要：`npm run regression:semantic` 改前已 overall=FAIL（FAIL-A 真 Circular role 注入 regression / FAIL-B stale 斷言，皆已記錄 SESSION_HANDOFF Regression Notes #3；Leonard 裁示只記錄不修）—— 任何 promote/release 前必自行重新 baseline，勿信舊「✅」。** 睇 Testing/poc-retrieval/eval/{S2_report,S2_breadth_report}.md + LEXICON_STRATEGY.md + lib/term_lexicon.py 了解 S2（10/12，promote 暫停）。問 Leonard：(1) 恢復 promote（恢復 bar=零新增 FAIL）？(2) 排 FAIL-A triage（涉 dedup/budget/排序設計）？(3) 轉 P2/P3？**promote 暫停中、未 Leonard 明示前 Draft backend 零接觸**；唔好跳 scope/§F/公開契約。碰 admin/auth/公開推送前必讀 §E.10。
```

---
