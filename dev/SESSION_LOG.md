# Session Log

<!-- Archives: dev/archive/ — entries moved when >400 lines or oldest entry >30 days -->

## 2026-06-03 Session 139 — 文件變更自動偵測 + 通知（detect+notify tier；code+CI+docs，0 data/Supabase mutation）

- **ID:** Claude_20260603_0959
- **Trigger:** Leonard 提功能需求「文件已 AI 分析+可追蹤頁數，下一步：知道文件變更就自動觸發工作」→ 我出設計建議 → Leonard 揀**最輕 tier「只升級偵測+自動通知」**（不自動 mutate/deploy）+「我先評估再定」MVP → 出 §3 PLAN → 兩個分叉揀建議方案（Hybrid hash + Ledger+Issue）
- **§3 Risk:** HIGH（改 load-bearing 監測腳本〔S126 chronic-fail 前科〕+ CI workflow + 外部 EDB GET）→ 出 PLAN + 設計分叉確認後入 CHANGE；本 tier 刻意排除破壞性鏈（無 fetch-into-vault / repage / Supabase / deploy）

### CHANGE（4 檔）
1. `dev/source/check_freshness.py`（重寫）：**Hybrid 兩層偵測** — Tier1 HEAD（Last-Mod/Content-Length/ETag）+ Tier2 raw-byte SHA-256 `content_hash`（authoritative，抑制 HEAD 假報）。`content_hash` 跟 metadata 同生命週期：只喺 write-sync 植入/更新；scheduled dry-run 對 baseline 偵測、不持久、保持平。判斷抽成純函數 `classify_change()` + 加 `--self-test`（離線 9 assertion）+ `--changes-out`（JSON 報告）+ `--ledger`（Markdown）+ `--limit`（測試）。原子寫入（temp+rename 防 registry 半寫腐爛）。**保留 exit 語義：changes 永不 fail，只 errors>threshold exit 1（S126 教訓）。**
2. `.github/workflows/freshness_check.yml`：`issues:write` + timeout 30（首次 write-sync 植 147 hash 一次性重）+ `--changes-out`/`--ledger` 接線 + **github-script 開/更新 Issue**（label `freshness-change`、try/catch 唔 mask 偵測成功、單一 Issue 不 spam）+ commit step 加 ledger（仍只 manual write-sync 觸發）。
3. `dev/source/FRESHNESS_GUIDE.md`：記 hybrid 偵測模型 + 新指令 + 通知/ledger + **Manual Gate Rule 不變**（偵測自動、re-ingestion 仍人手：URL re-discovery→mojibake pre-flight→repage→cb3_b2→SOURCE_SETS parity→deploy）。
4. `dev/DOC_SYNC_CHECKLIST.md`：加 row「Freshness monitoring / CI workflow change」（anti-pattern guard：無精確 row 必加）。

### QC / Test Scenarios（§3d）
| Scenario | Action | Expected | Actual | Result |
|---|---|---|---|---|
| 判斷邏輯 | `--self-test` 離線 | 7 logic + 2 ledger 全中 | ALL PASS | PASS |
| 穩態未變 | live dry-run --limit | 不報、零下載 | changes=0 hashed=0 | PASS |
| dry-run 不寫 registry | dry-run | registry 不變 | git status clean | PASS |
| write-sync 植 hash | --limit 2 write（temp 副本）| content_hash+hash_checked_at 寫入 | sag/coa 真 SHA-256 seeded | PASS |
| bootstrap 不報全變 | write-sync seed | changes=0（非「全部變更」）| changes=0 | PASS |
| 原子寫入 | write（temp 副本）| 無 .tmp 殘留、registry valid JSON | clean + valid | PASS |
| HEAD 假報抑制 | classify(cheap=T,hash 相同) | 不報 | (False,None) self-test | PASS |
| exit 語義 | code review | changes 不影響 exit | 只 errors>threshold exit 1 | PASS |
| YAML | yaml.safe_load | parse OK | OK | PASS |

- **獨立對抗覆核（Explore agent，唯讀）**：揪出 1 BLOCKER（registry 寫入無保護→腐爛風險）+ 2 MAJOR（github-script API 無 try/catch；new_hash null 未文檔化）→ **全部已修**（原子 temp+rename / try-catch+core.warning / 加 `hash_status` 欄）。覆核「bootstrap 報全變」aside 經實測證為誤判（以 self-test + seed 實測 changes=0 為準）。

### Sources changed
- `dev/source/check_freshness.py` / `.github/workflows/freshness_check.yml` / `dev/source/FRESHNESS_GUIDE.md` / `dev/DOC_SYNC_CHECKLIST.md`
- **NOT modified:** source_registry.json（hash 待首次 CI write-sync 植入）/ Supabase / knowledge.json / guidelines.json / app.html / backend / PROJECT_MASTER_SPEC / CODEBASE_CONTEXT
- 全部測試用 registry **臨時副本**，真 registry 零污染（驗 0 content_hash）。

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| Freshness monitoring / CI workflow change | FRESHNESS_GUIDE.md（done）/ CODEBASE_CONTEXT Directory Map（N/A — 無新 script 檔、同名腳本內部升級）/ SESSION_HANDOFF+LOG（done）| ✓ Done |
| New project doc trigger row | DOC_SYNC_CHECKLIST 加 row | ✓ Row added |

### 待辦 lesson（§8 monitoring）
偵測信號設計：HEAD metadata 太嘈（EDB redirect/re-export churn）→ content-hash 做 authoritative confirm 係正路；但 hash 生命週期必須同 metadata 一致（write-sync 植、scheduled dry-run 唔持久）先唔會每週 147 全 download。屬 monitoring，recurrence（其他 freshness-style 偵測）即 §8b promote。

### 同 session 後續 — 啟用 + mobile verify + SEN 修復（全部 live）
1. **✅ 啟用 freshness**（Leonard「1. 啟用」）：`gh` 未 auth → 本機背景跑全 write-sync。15 源計時探針 92s/0-error 確認可行 → 全 147 源：**147/147 hashed、0 error、0 failed**，7 源標 head-metadata drift（預期首跑：g10/g19/history_jss_2019 等近期 ingest 源）；ledger 生成；原子寫入無腐爛。commit `d96d56a` push。**自動偵測 live。** ⚠️ **教訓**：首次背景啟動誤用 `run_in_background:true` + `nohup … &` → 被追蹤 wrapper shell 因 `&` 即 exit 0、python detach（log 空、registry 0 seeded 嚇一跳）；實際 python 健康跑緊。改用純 `run_in_background` + `until [ -f json ]||!pgrep` 等待器正確監控。**run_in_background 唔好再加 `&`。**
2. **✅ mobile verify**：Leonard 真機確認手機「指引文件」UI 整體 OK（清 S136/S138 遺留）。
3. **✅ SEN「冇反應」根因 + 修復**（Leonard 報手機打「SEN」一直冇反應）：依「冇反應五因」卡先分層、對 live curl triage（非當邏輯 bug 改）。**根因 = Supabase 57014 transient statement-timeout**（free-tier pgvector probes=8，冷啟動第一 query 最易中）被 backend `wikiRepository` 包成 HTTP 400；**非** SEN route / CORS（ACAO=policychecker 正常）/ 前端 wiring。證據：warm 時「sen」「教師病假」全 200、「SEN」第一次（剛冷啟動）400 但 retry 3/3 即 200 出真內容。**修**：`backend/src/lib/wikiRepository.ts` searchWiki RPC 加 **retry-on-57014**（≤3 attempt、250/500ms linear backoff、只 retry `status>=500 && body含57014`、其他錯即拋、embedding 喺 loop 外不重算）。Leonard 揀此建議方案（vs 前端 retry / 調 Supabase）。typecheck+build exit 0；commit `13544d0` push → Render deploy → **post-deploy SEN smoke 6/6 PASS HTTP 200 帶真 SEN 內容**。
   - **§8b promote 候選**：57014 由「accepted transient」升級成「user-facing 失效」→ 已加 backend retry（regression-style fix）。recurrence / 其他 RPC 同類即考慮 promote SOP。cold-start mask 屬 logic-verified（warm smoke 6/6；真冷啟動 mask 留實際使用觀察）。

> 補充 commit chain S139：`dbef61a`（freshness code+docs）→`48d5308`（PERSIST）→`d96d56a`（啟用 seed+ledger）→`13544d0`（57014 retry）。Render 由 `13544d0` deploy。

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

⚠️ 然後讀 dev/HANDOFF_PACKAGE.md（可信狀態快照）。起手務必自行 verify git HEAD + knowledge.json._meta.stats vs SESSION_HANDOFF Current Baseline，並實測 egress（onrender /health，勿照抄）。S135-S139 證實 EDB + onrender + Supabase egress 均通；仍每次自測。

⚠️ Repo root = "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"（路徑含空格，shell 必須雙引號絕對路徑）。`python` 唔存在用 `python3`。git commit+push 由 Claude 做（指定檔勿 -A）。Agent team 係預設模式。回覆用中文。

S139 (2026-06-03)：**三件事全完成、live verified、0 outstanding bug**。HEAD origin/main = `eed168c`（起手自行 verify）。
(1) **文件變更自動偵測+通知** 建好＋啟用＋live：check_freshness.py 升級 Hybrid HEAD+content-hash（hash authoritative 抑制 HEAD 假報）+ classify_change 純函數 + --self-test(9) + 原子寫入 + 保留 exit 語義（changes 永不 fail，S126）；freshness_check.yml issues:write+timeout30+github-script 開/更新 freshness-change Issue + ledger commit。首次 write-sync 植 **147/147 content_hash（0 error）** + ledger。每週一自動偵測→開 Issue；**re-ingestion 仍人手閘**。
(2) **SEN「冇反應」修復**：根因 = Supabase **57014 transient statement-timeout**（冷啟動第一 query 最易中）被 backend 包成 HTTP 400；非 SEN route/CORS/前端。修 = `wikiRepository.ts` searchWiki RPC **retry-on-57014**（≤3 次 linear backoff、只 retry status>=500+body含57014、embedding 不重算）；deploy live、SEN smoke 6/6 PASS 200。
(3) **mobile #guidelines** Leonard 真機確認 OK。

Current objective and progress state:
- Baseline: Supabase ~9,912 / 103 marker-bearing / CB-3 final ceiling ~88% / brand live (policychecker.wongfu.net)（本 session data 層只 freshness content_hash seed，未動 Supabase chunks/knowledge）。
- freshness 自動偵測 live；57014 已加 backend retry；**0 outstanding bug**。

Pending tasks in priority order:
1. **下一階段方向（待 Leonard 明示）**：g14《校本資優培育課程指引》+ sen_curr_area + gifted_policy_docs（仍 0 chunks，SEN-adjacent，可補同 g10/g19 pattern）/ Q4 對外契約收斂（3 選項、敏感、**未明示勿掂**）/ §8b rule 2 automation / 39→148 guidelines。
2. **觀察（非阻塞）**：freshness 第一個 scheduled 週跑（週一 09:00 UTC）應正常偵測+開 freshness-change Issue；57014 retry 真冷啟動 mask 效果（warm smoke 已 6/6；cold-start mask = logic-verified）。
3. 既有 deferred backlog：§E.10(a) ACCEPTED conditional / FAIL-A record-only / stat_fact 2025/26 ROI≈0 / HKEAA。

Key files changed this session:
- freshness 功能：check_freshness.py / .github/workflows/freshness_check.yml / FRESHNESS_GUIDE.md / DOC_SYNC_CHECKLIST.md
- 啟用：source_registry.json（147 content_hash seed）+ dev/source/freshness_changes.md（NEW ledger）
- SEN 修：backend/src/lib/wikiRepository.ts（57014 retry）
- PERSIST：CODEBASE_CONTEXT / SESSION_HANDOFF / SESSION_LOG
- commit chain：`dbef61a`→`48d5308`→`d96d56a`→`13544d0`→`eed168c`（+closeout）。Render 由 `13544d0` deploy。

Known risks / blockers / cautions:
- 🟢 **0 outstanding bug**。freshness detect-only（scheduled=dry-run 安全、re-ingestion 人手閘）；57014 已 retry。
- 既有不變: 🔴 57014 transient(**S139 已加 backend retry**；exhaust 後仍 400、frontend 重試掣); FAIL-A(record-only); §E.10(a) ACCEPTED conditional; q.html/A·AB dormant 勿清; Q4 deferred 未明示勿掂; Stage-2 closed 勿復活; egress 每次自測; 路徑空格雙引號; wiki_chunks 欄名 `text` 非 `content`; 改 Draft code/data commit 必入 SESSION_LOG; init_backup gitignored。

Validation status:
- freshness: --self-test 9 PASS / 對抗覆核 1B+2M 全修 / 啟用 147/147 hashed 0 error / YAML OK。
- SEN 57014: typecheck+build exit 0 / post-deploy SEN smoke 6/6 PASS 200 帶真內容。
- mobile: Leonard 真機 OK。

Post-startup first action: 完成 §1 + HANDOFF_PACKAGE 起手序 + 自測（git HEAD=eed168c / knowledge facts 455 / onrender /health warm / egress）+ lazy-query playbook INDEX 後，問 Leonard 下一階段方向（g14+gifted SEN 補完 / Q4 契約〔敏感未明示勿掂〕/ §8b automation / 39→148）。可順手睇 GitHub 有冇開咗 freshness-change Issue。未 Leonard 明示前唔好自行掂 Q4 / reopen §E.10 / 動 Stage-2。
```

## 2026-06-02 Session 138 — 資料質素 backlog 執行：phys DROP + g10/g19 ingest + SEN route（生產 live + 0 regression）

- **ID:** Claude_20260602_1730
- **Trigger:** Leonard `/workflow 全做` 起手 → AskUserQuestion 三項全部明示授權：①SEN route 即做 / ②phys 即 DROP / ③g10/g19 要 ingest（S137 診斷 PLAN 落地）
- **§3 Risk:** HIGH（破壞性 Supabase mutation + code change + deploy + 多檔；criterion c/d）→ Leonard AskUserQuestion 三項授權 = confirmation；每個破壞性 op 前出 dry-run blast radius

### CHANGE（執行次序：phys DROP → g10 → g19 → SEN route）
1. **phys DROP**：`cb3_deprecate_stale.py --only phys_sss_2007_2015 --execute`（dry-run 確認 182 = S137 adversarial count）→ del=182 post=0 verified，audit log 寫 init_backup。Supabase 9,849→**9,667**。
2. **g10《特殊學校課程指引》(2024) ingest**：§E.12 URL re-discovery — registry `source_type=index`（index.html 導航頁 = 0 chunks 真 gap）→ crawl 揾返 attachment 直連 `CGSS (2024)_Full version_c.pdf`（25.7MB / 116p）。**mojibake pre-flight CLEAN**（特殊=152/課程=321/U+FFFD=0、proper text layer 非 phys CID-glyph）→ registry fix(url_primary 直連+source_type=pdf) + vault stub seed + repage Gate1 116=116 markers + cb3_b2 Gate2 **del=0 ins=129**（新源純 INSERT）。9,667→**9,796**。
3. **g19《全校參與模式融合教育運作指南》ingest**：§E.12 — registry `source_type=html`（wsa hub = 0 chunks gap）→ crawl 經 SENSE portal `sense.edb.gov.hk/.../integrated_education/landing/ie_guide_ch.pdf`（**2026年1月最新版** / 88p / 1.2MB）。mojibake CLEAN（融合教育=25/統籌主任=4/U+FFFD=0）→ registry fix(version 2024→2026-01) + stub + repage 88=88 + cb3_b2 **del=0 ins=116**。9,796→**9,912**。
4. **SEN dedicated route（searchChannelB.ts ~25 行）**：`TOPIC_KEYWORDS.sen`（`\bsen\b|\bsenco\b|特殊教育|特殊學校|融合教育|全校參與|統籌主任...` /i，**置 curriculum 之前** first-match）+ `SOURCE_SETS.sen=[g06,sag_2025_11,role_facts_student,role_facts_general,g10,g19]` + `QUERY_EXPANSIONS.sen`。鏡像 S118 PLAN-1b cpd/conduct route；routed→effectiveMinScore 0.08。

### QC / Test Scenarios（§3d）
| Scenario | Action | Expected | Actual | Result |
|---|---|---|---|---|
| phys 清理 | DROP phys | Supabase −182, phys=0 | 9,667, phys count=0 | PASS |
| g10 ingest | repage+migrate | del=0 ins≈full, clean | ins=129, FFFD=0 in SB | PASS |
| g19 ingest | repage+migrate | del=0 ins≈full, clean | ins=116, FFFD=0 in SB | PASS |
| 資料對賬 | total | 9849−182+129+116 | =9,912 ✓ | PASS |
| typecheck+build | npm check/build | exit 0 | exit 0 | PASS |
| SEN route 邏輯 | offline detect() 17 cases | sen 全中 + curriculum 不破 | 15/15 真 assert PASS（2「fail」係 test 期望錯：教師專業操守→conduct 係既有正確；sensible→null = \bsen\b false-positive guard 正確擋住） | PASS |
| live「sen」 | POST channel-b | route 去真 SEN 內容非 phys 亂碼 | g19 p=6/10/13 @0.76/0.75/0.72 + g06 SEN p=137/138 @0.72，全 FFFD=0 帶頁碼 | PASS |
| live「融合教育統籌主任 SENCO」 | POST | g19 SENCO 內容 | g19 p=13/10/57 @0.74 + g06 | PASS |
| live g10-specific | POST「特殊學校 校本課程 智障學生」 | g10 surface | g10 p=39 @0.697「為有特殊教育需要（如智障）學生調適課程」clean | PASS |
| regression「英文科課程指引」 | POST | route=curriculum 非 sen | music/pri_science/pe_kla/ma_kla（curriculum 完好） | PASS |

- 57014 transient 喺 live smoke 出現過一次、retry 即恢復（PMS §C.4 known、非 regression）。

### Sources changed
- `backend/src/api/searchChannelB.ts`（SEN route：3 處 SOURCE_SETS/TOPIC_KEYWORDS/QUERY_EXPANSIONS）
- `dev/source/source_registry.json`（g10 + g19 entry：url_primary 直連 PDF + source_type=pdf + notes §E.12）
- `dev/vault/repage_pdfs.py`（PILOT_LEGACY + PILOT_OUT 各 +g10/g19）
- `dev/vault/g10/extract_g10_repaged.txt`（NEW，116p）/ `dev/vault/g19/extract_g19_repaged.txt`（NEW，88p）
- **Supabase wiki_chunks**：9,849→9,912（−182 phys DROP / +129 g10 / +116 g19）
- commit `4048408` push origin/main → Render auto-deploy（backend SEN route live verified）
- **NOT modified:** knowledge.json / guidelines.json / app.html / frontend / PROJECT_MASTER_SPEC / CODEBASE_CONTEXT

### Doc Sync
Matched row: **Product behavior / tuning change** → SESSION_HANDOFF + SESSION_LOG（done）。CODEBASE_CONTEXT N/A（無 tech-stack/dir/external-service/Key-Decision 變；g10/g19 = 資料源非新基建、SEN route = 既有檔 tuning）。

### 同 session 後續 — 共用經驗庫（Playbook）接駁 + 初次 harvest（Leonard 指示，additive、scoped）
- **任務一（裝雙向 pointer）**：將跨-project「共用經驗庫 Playbook」(`/Users/leonard/Downloads/Claude Project/Leonard's playbook/playbook`) 嘅雙向 pointer 裝入本 project startup 檔 `AGENTS.md`（Handoff-Kit 4(a) 風格、3 處純 additive）：(A) 頂部 mandatory-startup marker 加 `§14`；(B) §1 startup 讀清單加第 5 步「lazy-query 該庫 INDEX.md、唔好讀晒所有卡」；(C) 檔尾新增 `## 14) 共用經驗庫（Playbook）` pointer block（本機 clone 路徑版、deposit 檔名 pre-fill `<日期>-policychecker-<短名>.md`）。**`AGENTS.md` 係 gitignored（私有治理檔、唔入 commit）→ 此 SESSION_LOG 記錄係 durable trace。** INDEX.md reachable 已驗。本 project 內部無同名 "playbook"、唔使 disambiguation。
- **任務二（一次性 harvest）**：翻睇本 project 經驗（SESSION_LOG/HANDOFF/memory/§E·§G lessons）+ dedup against 該庫 INDEX.md，提煉 **7 條可轉移教訓**寫成 inbox 提案（只丟 inbox、**唔掂 trunk**）：verify-load-bearing-state-not-docs (convention) / inspect-live-infra-before-ddl / dry-run-blast-radius-before-destructive-batch / throttled-api-not-empty-data / pdf-extraction-mojibake-triage / external-source-url-churn-rediscovery (patterns) / shell-cmd-abs-path-and-chain (convention)。每條皆有「幾時唔好用/例外」+ 出處。**Playbook repo commit `9fbd406`**（`inbox: policychecker 初次 harvest 提議 7 條`；提交時 trunk verified clean）。**收工時確認：該庫 librarian routine 已自動處理（commit `213814d` trunk 44→51）— 7 條提案全部 integrate 成 trunk 卡（5 patterns + 2 conventions），原 inbox 檔歸檔去 `inbox/_processed/`。** push 問題由 librarian 自動解決，無 pending。
- short name 拍板 = **policychecker**。0 EDB code/data/Supabase mutation（純治理檔 + 外部庫 inbox）。

### 待辦 lesson（§8 monitoring）
**§G.2 doc-drift 又中（Nth）：S137 交接寫 g10/g19 ingest「同 S135 history_jss PDF page-carry pattern」低估咗工作 — 實測 g10=`source_type=index`（導航頁）、g19=`source_type=html`（hub），兩者皆要 §E.12 URL re-discovery（crawl 揾返真 PDF）先得，非 plan 假設嘅「直接 fetch PDF」。** 兩者真 PDF 均 mojibake pre-flight CLEAN（phys 教訓落實：ingest 前必驗 text layer）。Sub-agent egress 教訓：背景 general-purpose agent 嘅 Bash/WebFetch/WebSearch 被 deny → egress-heavy discovery 要主 agent 自己做。

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

⚠️ 然後讀 dev/HANDOFF_PACKAGE.md（可信狀態快照）。起手務必自行 verify git HEAD + knowledge.json._meta.stats vs SESSION_HANDOFF Current Baseline，並實測 egress（onrender /health，勿照抄）。S135-S138 證實 EDB + onrender + Supabase egress 均通；仍每次自測。

⚠️ Repo root = "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"（路徑含空格，shell 必須雙引號絕對路徑）。`python` 唔存在用 `python3`。git commit+push 由 Claude 做（指定檔勿 -A）。Agent team 係預設模式。回覆用中文。

S138 (2026-06-02)：**S137 資料質素 backlog 三項全部執行落地、生產 live、0 regression**。Leonard AskUserQuestion 三項全授權。
- ✅ phys_sss_2007_2015 182 CID-glyph 亂碼 chunks **DROPPED**（cb3_deprecate_stale.py，reversible audit log）。
- ✅ g10《特殊學校課程指引》(2024, 116p) + g19《全校參與模式融合教育運作指南》(2026-01, 88p) **ingested**（皆 §E.12 URL re-discovery：g10 registry 係 index.html 導航頁、g19 係 wsa hub html → crawl 揾返真直連 PDF；兩者 mojibake pre-flight CLEAN；del=0 純 INSERT +129/+116）。
- ✅ SEN dedicated route 入 searchChannelB.ts（TOPIC_KEYWORDS.sen 置 curriculum 前 + SOURCE_SETS.sen + QUERY_EXPANSIONS.sen）→ commit 4048408 push → Render deploy → **live「sen」route 去 g19/g06 真 SEN 內容 @0.71-0.76 帶頁碼、phys 亂碼消失**。
- **Supabase 9,849→9,912**（−182 +129 +116）。103 marker-bearing（102 − phys DROP + g10 + g19）。

Current objective and progress state:
- Baseline: Supabase 9,912 / 103 marker-bearing / CB-3 final ceiling ~88% / brand live (policychecker.wongfu.net)
- 資料質素 backlog（S137 診斷）= 全部執行完、live verified。無 pending 子任務。
- **共用經驗庫 Playbook 已接駁**：AGENTS.md §14 雙向 pointer（開工 lazy-query `…/Leonard's playbook/playbook/INDEX.md`、收工夠成熟先丟 inbox 提案、deposit 檔名 `<日期>-policychecker-<短名>.md`）。S138 初次 harvest 7 條已被 librarian integrate 入 trunk。**下個 session 起手記得 lazy-query 該庫 INDEX**（AGENTS.md §1 第 5 步、§14）。

Pending tasks in priority order:
1. **🔵 Leonard 真機 verify pending（S136 遺留）**：手機「指引文件」tab（#guidelines mobile render）+ Channel B 政策搜尋 policychecker.wongfu.net；可順手再驗「sen」家陣應出 g19/g06 真 SEN 內容。
2. **下一階段方向（待 Leonard）**：Q4 對外契約收斂（3 選項、未明示勿掂）/ §8b rule 2 automation / 39→148 guidelines 擴展。
3. 既有 deferred 不變：§E.10(a) ACCEPTED conditional / 57014 transient / FAIL-A record-only / Stage-2 closed / stat_fact 2025/26 ROI≈0 / g14《校本資優培育課程指引》+ sen_curr_area + gifted_policy_docs 仍 0 chunks（SEN-adjacent gap，本次未做、待 Leonard 決是否補）。

Key files changed this session:
- backend/src/api/searchChannelB.ts（SEN route）/ dev/source/source_registry.json（g10+g19）/ dev/vault/repage_pdfs.py / dev/vault/g10|g19/*_repaged.txt（NEW）；commit 4048408 + PERSIST 8a7a3e1 + playbook record b17defc。
- Supabase mutation：phys DROP −182、g10 +129、g19 +116。
- AGENTS.md §14 共用經驗庫 pointer（gitignored、唔入 commit、記喺 SESSION_LOG）+ 外部 playbook repo inbox 7 提案（已 librarian integrate）。

Known risks / blockers / cautions:
- 🟢 SEN route + g10/g19 live verified；g19 多數 query #1（operational guide 最 dense），g10 為特殊學校-specific query surface（p=39 @0.697），g06 SEN sections 穩定 surface — 全 clean 帶頁碼。ranking 競爭非 regression。
- 既有不變: 57014 transient(retry 即恢復); FAIL-A(record-only); §E.10(a) ACCEPTED conditional; q.html/A·AB dormant 勿清; Q4 deferred 未明示勿掂; Stage-2 closed 勿復活; egress 每次自測; 路徑空格雙引號; 改 Draft code/data commit 必入 SESSION_LOG。
- 🔴 phys mojibake = CID glyph-index、不可 decode（已 DROP 解決）；wiki_chunks 欄名 `text` 非 `content`；init_backup gitignored（backup/audit log 唔入 commit）。

Validation status:
- 起手自測全 PASS：git HEAD=b17defc==origin/main（tree clean）/ knowledge facts=455 / onrender /health warm cache_a=455 / CORS policychecker ACAO / Supabase wiki_chunks=9,912（g10=129 g19=116 phys=0）。
- live SEN smoke 5/5 query PASS（sen/特殊學校課程/融合教育SENCO/g10-specific/curriculum-regression）全 clean 帶頁碼、curriculum route 不破。
- typecheck+build exit 0；SEN route offline detect() 真 assert 全 PASS。

Post-startup first action: 完成 §1（含**新第 5 步：lazy-query 共用經驗庫 `…/Leonard's playbook/playbook/INDEX.md`**，撞 trigger 先開卡）+ HANDOFF_PACKAGE 起手序 + 自測（git HEAD=b17defc / knowledge facts:455 / Supabase 9,912 / egress onrender /health / CORS policychecker ACAO）後，問 Leonard 下一步方向（S137 資料質素 backlog 已全清）：(1) 是否補埋其餘 SEN-adjacent 0-chunks 源（g14 資優 / sen_curr_area / gifted_policy_docs）；(2) Q4 對外契約收斂；(3) 39→148 guidelines 擴展。未明示前唔好自行掂 Q4 / reopen §E.10 / 動 Stage-2。
```
