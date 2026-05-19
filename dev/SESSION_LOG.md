# Session Log

<!-- Archives: dev/archive/ — entries moved when >400 lines or oldest entry >30 days -->

## 2026-05-19 Session 119 — Channel-B-only 搜尋 surface（Phase 1 promote）：全 user-facing A/AB access 移除（檔案 dormant、契約零接觸）

- **ID:** Claude_20260519_1801
- **Summary:** Leonard live-test S118 PLAN-1b 5 query（CPD/幼稚園收生/體罰/STEAM/接收警告信後果）→ 一致裁定：Channel B 明顯最好、Channel A 太多雜訊、A+B 被 A 拖累（實證確認既有 FAIL-A/§E.11）。策略決定：**搜尋介面行 Channel-B-only**（全 user-facing 移除 A/AB，檔案留 dormant）；Q4（Channel A→`knowledge.json` 對外契約）= 解耦獨立 track、日後成熟再議；CB-3 頁數可追溯＝北極星、結構上只 B 可做，Phase 2 診斷 next。
- **§3 HIGH-risk 正常流程（非 §2 rule6 override）：** 出完整 PLAN（5 surface inventory + §3d matrix）→ Leonard 明確確認「同意做」，含 scope 修正（q.html/index.html 亦去 access link、檔案 dormant；文案對齊；知悉 t-purchase B-only 較深）。PLAN→confirm→CHANGE 正常 §3，無 rule6 衝突。
- **CHANGE Phase 1（5 前端 surface，全最小可逆）：** `app.html`（`searchChannel` default 'A'→'B'；`CHANNEL_OPTS`=[B]；selector gated `length>1` 隱藏；stale「2,874」→「10,736 個 EDB 原文知識片段」）；`index.html`（footer q.html link 刪；ftags 已核實/合併→EDB原文/語義/整理；hero 252・feature 307・flow 366 文案去 Channel-A 框架剩 EDB 原文）；`t-purchase.html`（src-ctrl 3 radio→單一 B checked「EDB 原文來源」；`selectedChannel()` fallback 'AB'→'B'；src-card q.html link 刪）；`mobile.js`（`/api/search/combined`→`/api/search/channel-b`、body 去 `enable_topic_filter`；nav `match`/isActive 去 'q.html'）。
- **零接觸（dormant/可逆）：** backend `/channel-a` `/combined` endpoint、`searchChannelB.ts`、`knowledge.json`/`guidelines.json` 對外契約、`q.html` 檔案本體（14226B 留存，只去 inbound link）、app.html/t-purchase A·AB code path（gated dormant）。Q4 deferred = Channel A 管道照常餵 `knowledge.json` 予下游，未郁。
- **Verified/QC:** `git status`=只 4 前端檔；契約+backend zero-diff；B-only grep 0 residual（無 q.html/value=A/AB//combined/channel-a）；q.html 留檔；app.html `{}`/`()` 平衡 invariant 與 clean HEAD **完全一致**（無新增 imbalance）；`npm run check`✅`build`✅（前端改動零 backend 耦合）；`regression:semantic` overall=FAIL 但 **delta=0 new**（PASS9/notes1/FAIL2 = 既有 FAIL-A finance_distinct + FAIL-B schema 1.3.1 stale，record-only，與 S117/S118 一致，未碰 backend/knowledge）。§3d 5/5（4 靜態 PASS + 正常流程靜態 PASS／渲染依 §D.7/§G.2 鎖定方法論交 Leonard；**後 Leonard browser-verify PASS 2026-05-19 = Phase 1 完全 closed**）。
- **Pending:** Phase 2 CB-3 頁數診斷（唯讀：sample live `/channel-b` page 命中率 + inspect `build_wiki_index.py`/Supabase corpus `=== Page N ===`）→ 根因 + 3 scope 選項回 Leonard。前端改動 push 後 GitHub Pages auto-deploy；Leonard browser-verify。
- **Next:** 接手＝Phase 1 promote+commit+push；做 Phase 2 唯讀診斷出 scope 選項；Q4 deferred 勿自行掂；Stage-2 仍 closed 勿復活。

#### CB-3 Phase 2 診斷 + Option B（同一 session 續）
- **Phase 2 唯讀診斷（實證根因）：** live `/channel-b` 多 query `page` 命中 0/N → 根因＝**語料 provenance**（UI/後端已 work：`SourcesAccordion` app.html:2736 有頁顯示、`extractFirstPage` regex 正確）。全庫 **113 vault extract，39 有 `=== Page N ===` 標記、74 無**（視抽取 pipeline）；Leonard 測試高流量源 `sag_2025_11`/`g06`/`g04`/`g26`/`g25`=0 標記、`g05`=30。出 3 scope 選項（A 無得修／B 後端容錯+chunk帶頁／C 全重抽）；Leonard 揀 **B（試B再看結果）**。
- **Option B §3 HIGH-risk PLAN（Leonard 確認）：** 分 B-1（本地可量、零外部 mutation）→ B-2（生產 re-embed + Supabase DELETE/replace 39 源，**閘控於 B-1 結果 + Leonard 明示**）。chunk id=`vault_{src}_{texthash}` → 改文字＝新 id → upsert 並存舊孤兒 → B-2 必須 DELETE-by-source_id 替換（§E.7/§E.13 紀律）。
- **CHANGE B-1（Draft）：** `dev/vault/build_wiki_index.py` +`PAGE_MARKER_RE`（match 後端 extractFirstPage regex）+`chunk_text_with_page_carry()`（carry last-seen `=== Page N ===` 落欠標記 chunk；marker 前 chunk 不變；**無標記源 byte-identical → hash/id 不變 → 74 源零影響**）；vault loop call 換新 helper。最小 additive、零後端/Supabase schema 改（§E.13-safe）。
- **B-1 量度（離線，無 embed/upload/不寫 wiki_index.json；harness＝Testing/poc-retrieval/eval/cb3_b1_pagecarry_measure.py 非 git）：** 39 標記源 **全部 100% chunk 帶頁**（before partial→after 100%）；全庫 vault page-resolvable **13.2%→23.7%，+1017 chunk**；**INVARIANT PASS：74 無標記源 0 changed（byte-identical）**；spot-check circ_edbc24017/g01/g05 carried page 正確。
- **誠實 B vs C ceiling：** B 乾淨救 39 源（curriculum guides/circulars/g01-g05/stat_enrolment），但 **Leonard 測試嗰啲高流量 admin 源（sag_2025_11/g06/g26）無標記＝B 救唔到、仍要 Option C 重抽**。B 係 necessary-not-sufficient；達北極星全覆蓋仍需 C。
- **B-1 狀態：** code 落 Draft + commit（inert）；B-2 GATED。

#### CB-3 B-2 生產落地（Leonard informed go「照修正後外科式 B-2 執行」）
- **§3 divergence #1（執行前）：** dry-run 揭 `build_wiki_index.py` hash-dedup vs live 語料失效（8315「new」）→ 原「跑 build 再 upload」前提錯。改用**專用 39-源 driver** `dev/cb3_b2_pagecarry_migrate.py`（canonical `chunk_text_with_page_carry` + update_g04 式 per-source DELETE/upload，繞過失效 dedup）。read-only dry-run 出確切 blast：39 源 DELETE 2807→INSERT 2297、net −510（stat_enrolment re-chunk 正常化）、~$0.05；披露後 Leonard 明示執行。
- **§3 divergence #2（執行中）：** 首輪 25 源（課程/通告/g0x）乾淨完成（live 確認 g05 體罰 p=30/30/18），但 `stat_enrolment_2012` upload 撞 **409 duplicate pkey** → DELETE 113 後 0 upload＝**該源生產變空**。根因：driver `build_rows()` 漏咗 `upload_wiki_to_supabase.py` 已有嘅 `seen_ids` intra-source 去重（stat 表格重複文字→同 sha256→同 id）。依 §3 停、唯讀診斷確認 blast contained（25 done 正確、stat_2012 空、13 未動、74 marker-less + role/stat/guide 零影響、local wiki_index.json 未改），報 Leonard。
- **復原（Leonard 揀「修 dedup + 補做剩低 14 源」）：** driver 加 `seen_ids` 去重 + `--only` scope + `--skip-local`（部分 run 唔寫 local 免 mixed artifact，Supabase 為 query-authoritative）。dry-run 自驗 14 源 deduped（stat 59→55 等）→ `--execute --only <14> --skip-local`：14 源全 del/ins/now OK（stat_2012 0→55 復原、stat_2013-24 deduped、va_p1_s6_2024 86→86）。DELETED 1063→INSERTED 614。25 done 未再掂。
- **QC（唯讀 verify + live smoke）：** total wiki_chunks=10606 內部一致；recovered（stat_2012=55/stat_2024=34/va=86）+ first-run（g05=29/circ=12/eng_pri=275）+ marker-less control（sag=415/g06=300/g26=23 未掂）全對。live smoke：採購程序→g01 **p=5/p=1**、教師專業操守→g05 **p=30/16/9**、視覺藝術評賞→va **p=27/52**，相關度 0.59-0.67 健康＝**page-prefix 無拉低 retrieval**。一次 採購程序→0 經 retry 即恢復＝已知 free-tier `57014`/冷啟 transient（非 B-2 regression，§3 已查實）。
- **§8 固化（incident→rule）：** 寫新 Supabase upload path 必須**完整** reuse `upload_wiki_to_supabase.py` 嘅 `seen_ids` 去重 + per-source DELETE/replace pattern，唔可只抄一半（已 fire 過＝生產 1 源變空 + rework；recurrence-prone：codebase 已有 3 套 divergent chunker）。入 PROJECT_MASTER_SPEC §E.14 + §D.15。
- **已知 drift（誠實記）：** local `wiki_index.json` 對 39 page-carried 源 vs Supabase **已 diverge**（Supabase query-authoritative；local 留全-old 內部一致，非 mixed；reconcile = 低優先 backlog，非生產影響）。build_wiki_index hash-dedup vs live 語料不對齊＝latent corpus-consistency（非本 scope，記 backlog）。
- **B-2 狀態：** ✅ 全 39 marker 源 page-carry 生產 live + verified。
- **Session CLOSED 2026-05-19（Leonard「收工」）** — §4 closeout 完成。Phase 1（5 surface B-only + Leonard browser-verify PASS）+ CB-3 Option B（B-1 page-carry + B-2 外科 39 源生產 replace，含 stat 409 incident 修+復原、§8 固化 §E.14）全完成生產 live；全部 commit+push（HEAD 同步 origin/main）；§4a apply（SESSION_LOG 490→157，5 條封存 dev/archive/SESSION_LOG_2026_Q2.md，保留 S119/S118）。下次起手＝問 Leonard 排 **Option C**（74 無標記源，唯一 open next）。

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| Product behavior / tuning change（Channel-B-only 搜尋 surface）| SESSION_HANDOFF baseline/Open-Priorities-regen/risks/record + SESSION_LOG 本 entry + QC evidence | ✓ Done |
| Long-term spec / locked decision / architecture invariant change（推翻雙通道搜尋 surface 鎖定決策）| PROJECT_MASTER_SPEC §F.2/§F.6/§F.9 + §B.1/§B.5 + §A.2；CODEBASE_CONTEXT Key Decisions 方向 shift；SESSION_HANDOFF baseline | ✓ Done |
| External API / service change | CODEBASE_CONTEXT External Services block＝**N/A**（Supabase/backend endpoint 無變；前端只係唔再 call /combined·/channel-a）；Directory Map app.html/q.html/index.html channel-surface 註 + AI Maintenance Log +S119 | ✓ Done（Log/Map）/ block N/A |
| Doc carrying now-stale "two-channel search surface" | PROJECT_MASTER_SPEC §F；auto-memory project_direction_review（B-only 方向 + Q4 deferred track + CB-3 next）+ MEMORY.md | ✓ Done |
| Product behavior / tuning change（CB-3 Option B B-1：build_wiki_index.py page-carry）| SESSION_HANDOFF baseline/Open-Priorities/record + SESSION_LOG 本 entry CB-3 block + B-1 量度 evidence | ✓ Done |
| Long-term spec / locked decision / architecture invariant change（CB-3 page-traceability 機制：chunk page-carry）| PROJECT_MASTER_SPEC §C.4·§E.13 caveat + §D 新方法；CODEBASE_CONTEXT build_wiki_index.py 註 + AI Maintenance Log +S119-CB3；auto-memory project_direction_review CB-3 進展 | ✓ Done |
| New / iterated isolated PoC (Testing/ only) | Testing/poc-retrieval/eval/cb3_b1_pagecarry_measure.py + cb3_b2_dryrun.py（非 git）；Draft `git status` 無 PoC 檔外洩 | ✓ Done |
| Product behavior change（CB-3 B-2：39 源 Supabase page-carry replace 生產落地）| SESSION_HANDOFF baseline/Open-Priorities/risks/record + SESSION_LOG B-2 block + 唯讀 verify + live smoke evidence | ✓ Done |
| Regression + Lessons-to-Rule（§8 incident：driver 漏 proven seen_ids dedup → 生產 1 源變空 + rework）| PROJECT_MASTER_SPEC §E.14（新失敗教訓）+ §D.15 註（完整 reuse upload_wiki_to_supabase dedup/per-source-replace pattern）；本 SESSION_LOG §8 固化段 | ✓ Done |
| External API / service change（Supabase wiki_chunks 39 源 row 內容/數量變；REST DELETE+POST 經 service key）| CODEBASE_CONTEXT External Services 仍 N/A（Supabase 服務本身無變、無 schema/RPC DDL；只 data rows）；AI Maintenance Log +S119-CB3-B2；§0b：transport=update_g04 proven REST pattern（已記 SESSION_LOG/PMS）| ✓ Done（Log/§0b）/ block N/A |
| Doc-drift / known divergence（local wiki_index.json vs Supabase 對 39 源 diverge）| SESSION_HANDOFF risks + 本 SESSION_LOG「已知 drift」段（Supabase query-authoritative；reconcile=低優先 backlog）| ✓ Done |

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

⚠️ 然後讀 dev/HANDOFF_PACKAGE.md（可信狀態快照）。起手務必自行 verify git HEAD + knowledge.json._meta.stats vs SESSION_HANDOFF Current Baseline，並實測 egress（onrender /health，勿照抄）。

⚠️ Repo root = "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"（路徑含空格，shell 必須雙引號絕對路徑）。Channel B/retrieval PoC 喺姊妹資料夾 "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Testing/poc-retrieval/"（唔喺 git、Draft 零接觸）。`python` 唔存在用 `python3`。git commit+push 由 Claude 做（指定檔勿 -A）。Agent team 係預設模式。回覆用中文。

S119（CLOSED 2026-05-19，Leonard「收工」）：Leonard live-test 後定方向＝**搜尋介面 Channel-B-only**。**Phase 1 全完成 closed**：5 前端 surface（app.html/index.html/t-purchase.html/mobile.js）移除 user-facing A/AB、檔 dormant 可逆、backend endpoint/`knowledge.json` 對外契約零接觸（Q4 deferred）；QC PASS + **Leonard browser-verify PASS 2026-05-19**。**CB-3 頁數 = Option B 全做完生產 live**：診斷根因＝語料 provenance（39/113 vault 有頁標記）→ B-1（`build_wiki_index.py` `chunk_text_with_page_carry()`，39 源 100%帶頁、74 源 byte-identical 不影響）→ B-2 專用 driver `dev/cb3_b2_pagecarry_migrate.py` 外科 per-source DELETE/replace 39 源（25 首輪 + 14 復原；中途 `stat_enrolment_2012` 409 incident 已修 seen_ids dedup + scoped 復原；§8 固化 §E.14）。live smoke：採購→g01 p=5/1、操守/體罰→g05 p=30/16/9、視覺藝術→va p=27/52，相關度 0.59-0.67 無 regression。全部 commit+push、HEAD 同步 origin/main。

Current objective and progress state:
- Phase 1 Channel-B-only surface＝**完成 closed**（promote+QC+commit/push + Leonard browser-verify PASS 2026-05-19）。
- CB-3 Option B＝**B-1 + B-2 全完成、生產 live verified**：全 39 marker 源 page-carry，Supabase wiki_chunks total=10606 內部一致，marker-less + role/stat/guideline 零影響。
- **已知 drift（誠實，非生產影響）：** local `wiki_index.json` 對 39 源 vs Supabase diverge（**Supabase query-authoritative**；local 留全-old 內部一致非 mixed；reconcile=低優先 backlog）。build_wiki_index hash-dedup vs live 語料不齊＝latent corpus-consistency（backlog，非本 scope）。
- Q4（Channel A→`knowledge.json`→下游 Circular System 契約）＝deferred 獨立 track（3 選項，未明示勿掂）。Stage-2 adaptive combo closed-as-non-viable 勿復活。

Pending tasks in priority order:
1. **Option C — CB-3 北極星全覆蓋（唯一 open next，問 Leonard 排）**：74 無標記源（含高流量 `sag_2025_11`/`g06`/`g04`/`g26`/`g25`，正係 Leonard 測試 query 命中嗰啲）重抽取頁標記 + 外科式 replace（可重用 `dev/cb3_b2_pagecarry_migrate.py`，**必守 §E.14 完整 reuse pattern**）。HTML-landing 源結構上永無 `#page=N`（天花板）。
2. CB-3 收尾 backlog（低優先，非生產影響）：local `wiki_index.json`↔Supabase reconcile；build_wiki_index hash-dedup vs live 不齊。
3. 既有 deferred：🔴 Supabase `57014` timeout / probes=8 live 未獨立 introspect（SQL 已備）；🔴 §E.10 admin-login security；🔴 FAIL-A Circular 注入 regression（record-only）；P2 分類148/P3；Mobile UI P2；HKEAA；FAIL-B `semanticRegression.ts:292` stale 1.3.1。
4. Q4 對外契約收斂（deferred 獨立 track，B-only+CB-3 成熟後 Leonard 排）。

Key files changed this session (全部 commit+push)：
- Draft：app.html / index.html / t-purchase.html / mobile.js（Phase 1 Channel-B-only）；`dev/vault/build_wiki_index.py`（CB-3 B-1 page-carry）；`dev/cb3_b2_pagecarry_migrate.py`（B-2 driver，含 seen_ids dedup / --only / --skip-local / --dry-run 預設）；dev/SESSION_LOG / SESSION_HANDOFF / PROJECT_MASTER_SPEC / CODEBASE_CONTEXT；§4a → dev/archive/SESSION_LOG_2026_Q2.md。
- Supabase wiki_chunks（生產，已 live verified）：39 marker 源 row page-carry replace（非 git）。
- Testing/poc-retrieval/eval/：cb3_b1_pagecarry_measure.py、cb3_b2_dryrun.py（非 git）。
- auto-memory（repo 外）：project_direction_review.md、MEMORY.md。

Known risks / blockers / cautions:
- **§E.14 §8 教訓**：寫任何新 Supabase `wiki_chunks` upload path 必須**完整** reuse `upload_wiki_to_supabase.py`（seen_ids by-id dedup + per-source DELETE-by-source_id 再 insert + canonical build_wiki_index chunker），唔可只抄一半（已 fire＝生產 1 源變空 + rework）。Option C 重用 driver 時必守。
- local `wiki_index.json` vs Supabase 對 39 源 diverge（Supabase query-authoritative；reconcile 低優先 backlog，非生產影響）。
- B ceiling：39 標記源已救；74 無標記（含 sag/g06/g26 高流量、Leonard 測試 query 命中）仍無頁＝需 Option C；HTML-landing 永無 `#page=N`。
- Supabase free-tier 偶發 `57014`/冷啟 transient（retry 即恢復，非 regression）；🔴 probes=8 live 未獨立 introspect；🔴 §E.10；🔴 FAIL-A（record-only）；§3c regression 既有 FAIL-A/B record-only。
- 檔案 dormant 非刪（q.html/A·AB code path/backend `/channel-a`·`/combined` endpoint 全可逆，勿當 dead code 清）；Q4 契約 Channel A 管道照常餵下游未郁，未 Leonard 明示勿掂契約/下游；Stage-2 closed 勿復活。
- egress 間歇每次自測（onrender /health 勿照抄）；路徑含空格 shell 必雙引號絕對路徑；Testing/ 喺 Draft git 外；改 Draft code/data commit 必入 SESSION_LOG（已遵）。

Validation status:
- PASS Phase 1：契約+backend zero-diff；B-only grep 0 residual；app.html JSX 平衡 invariant＝clean HEAD；npm check/build ✅；regression:semantic delta=0 new（既有 FAIL-A/B record-only）；**渲染 Leonard browser-verify PASS 2026-05-19 = closed**。
- PASS CB-3 B-1（離線量度）+ B-2（生產 live）：39 源 page-carry、per-source count verify OK、live smoke 多 query 頁碼出+相關度 0.59-0.67 健康、marker-less control 未掂、Supabase total 10606 一致。
- OPEN（非 pending-blocker）：Option C 未做（等 Leonard 排）；local↔Supabase reconcile（低優先 backlog）；Q4 deferred；Stage-2 closed。

Post-startup first action: 完成 §1 起手序 + HANDOFF_PACKAGE + 自測（git HEAD / knowledge.json._meta.stats vs baseline / egress 實測）後，**S119 已 closeout — Phase 1 全完成 closed + CB-3 Option B（B-1+B-2）全完成生產 live ——第一件事＝問 Leonard：CB-3 推唔推 Option C（74 無標記源含 sag/g06/g26 高流量；達北極星全覆蓋；可重用 `dev/cb3_b2_pagecarry_migrate.py`，必守 §E.14）？** 未 Leonard 明示前**唔好自行做 Option C / local↔Supabase reconcile / 掂 Q4 契約/下游 / 復活 Stage-2 / 改其他 Draft**。碰 admin/auth/公開推送前必讀 §E.10。CB-3 / B-only 方向 / Q4 track / §8 incident 詳見 auto-memory project_direction_review。
```

---

## 2026-05-19 Session 118 — Stage 2 combo 判定非可行（雙獨立驗證）→ pivot PLAN-1b：4 條 selective route promote（fixed cutoff）

- **ID:** Claude_20260519_1300
- **Summary:** Leonard `/goal A` 批 Stage 2 Scope A（combo adaptive cutoff）。出 §3 HIGH-risk PLAN（agent-team groundwork）→ pre-CHANGE offline acceptance gate **FAIL**：combo regress 病假/體罰/幼稚園收生/STEAM。獨立 audit **確認 FAIL 真**（非 harness bug；根因＝上游 ranking defect，正確 gold 排喺高分噪音之下，cutoff 結構上救唔到）。依 §3 偏離 + PLAN「FAIL→stop、唔 ship regression」停 CHANGE。§2 rule 6 衝突（/goal A vs no-ship-regression）報 Leonard → dismiss「do not proceed, wait」→ 其後「我不知道點決定，你按最終目標選擇及行動，直至/goal」＝授權自主。按最終目標（北極星＝正確改善檢索）pivot **PLAN-1b**。
- **PLAN-1b（agent-team 落手，全 Testing/ 先）：** feasibility 診斷根因（CPD＝純 allowlist-gap：gold 喺 sag_2025_11/g06 唔喺任何 SOURCE_SET；體罰/STEAM/幼稚園收生＝within-allowlist mis-rank）→ 建 4 條 dedicated selective route（cpd/kg_admission/conduct/steam，first-match，dedicated tight set 穿過 §E.3 SAG-exclusion 針孔）+ selective expansion（單一 QUERY_EXPANSIONS、§D.9/§3b 一規一處）。**獨立 audit：** worker 數學 faithful，但「OVERALL PASS」對 **病假 overstated**（病假 combo 仍 .25＝combo 對病假仍 regress、PLAN-1b 無掂）；§E.3 SAG≤3（quota cap=3）closed；8 條 unchanged 無 hijack；STEAM/體罰 lift global-rank-8 脆弱 flag。**Live-verify（dedicated /channel-b 真 probes=8）：** 4 route 可救 gold 全部 live surface（體罰§58 r9、STEAM r8、CPD/幼稚園收生 r1），offline 無高估 → live-robust。
- **裁定：** Stage 2 adaptive combo＝**正式放棄**（病राhard regression 兩獨立驗證；PLAN-1 promote 不用 adaptive threshold）。PLAN-1 真正得益＝**promote PLAN-1b 4 route（fixed cutoff）**：CPD 0→0.8、幼稚園收生/體罰/STEAM 改善、12 條零回歸、§E.3-safe、live-verified。
- **CHANGE（Draft）：** `backend/src/api/searchChannelB.ts` — SOURCE_SETS +cpd/kg_admission/conduct（dedicated tight sets，SAG 由 per-source quota 約束）、TOPIC_KEYWORDS +4 route（first-match 置頂）、QUERY_EXPANSIONS +4（同一 map 無 fork）。**min_score/effectiveMinScore 不動（fixed cutoff 保留）、無 combo、唔掂 S117 masking 契約。**
- **§2 rule 6 OVERRIDE record:** PLAN-1b promote＝Draft external-integration＝§3 HIGH-risk，常規須 Leonard PLAN-confirm。Leonard 明確 standing 授權「按最終目標選擇及行動直至/goal」+ agent-team（feasibility/獨立audit/monitor/live-verify 四重）為控制 + live test-verify 完成 → 視為授權；risk 已述、scope 最小、git-reversible、fixed-cutoff only。按 §2 rule 6 comply + 此 record（+ SESSION_HANDOFF）。
- **Verified/QC:** routing harness 12/12（4 新 route 對 + 8 unchanged 無 hijack）；`npm run check`✅`build`✅；`regression:semantic` overall=FAIL 但 **delta=0 new**（既有 FAIL-A/B record-only 未碰；7 topic-routing + 2 retrieval 全 PASS＝topicDetector/Channel-A 不受影響）。offline acceptance grade（獨立 audit + live-verify 雙重）＝行為驗收證據。
- **新風險（記）：** live-verify 5 RPC 有 2 個 HTTP400 / Supabase `57014` statement-timeout（retry 後成功）— free-tier Postgres 喺 probes=8 偶發 timeout，**生產可用性**問題（與檢索正確無關；S117 修好令真錯誤正確浮面成 error 非假「未配置」＝觀測性 working）。
- **Pending:** PLAN-1b promote 已落 Draft+QC+commit+push；**post-deploy smoke 確認 cpd route 生產 live**（q=CPD → source_ids {sag_2025_11:3,g06:3,role_facts_hr:2}、SAG quota cap=3、未 degraded）。probes=8 *live* 仍未獨立 `pg_get_functiondef` introspect（唯讀 INSPECT SQL 已交 Leonard、未跑）；Stage 2 combo 放棄；病假 combo-regression＝known（非本 promote 範圍，fixed cutoff 下 病假=.5 無回歸）。
- **Next:** 接手＝PLAN-1b 4 route 已 promote+verified+生產確認；問 Leonard：(a) 跑唯讀 probes=8-live INSPECT？(b) Supabase free-tier probes=8 `57014` timeout 要否處理（生產可用性）？(c) 病假 combo-gap＝future PLAN-1c 抑或接受 fixed-only / 推進 CB-3（北極星頁數）？
- **Session CLOSED 2026-05-19（Leonard「收工」）** — §4 closeout 完成；Stage-2 goal-A closed-as-non-viable（雙獨立驗證）；PLAN-1b shipped+生產確認；HEAD `84033b1` origin/main 同步。下次起手＝問 Leonard 排 (a)probes-INSPECT/(b)Supabase timeout/(c)CB-3·病राgap。

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

S118：Stage 2 adaptive combo 經雙獨立驗證**判定非可行並放棄**（病राhard combo-regression，根因＝上游 ranking defect）。Leonard 授權「按最終目標選擇及行動直至/goal」→ pivot 並 promote **PLAN-1b**：`searchChannelB.ts` 加 4 條 dedicated selective route（cpd/kg_admission/conduct/steam，first-match，dedicated tight set + 單一 QUERY_EXPANSIONS expansion），**fixed cutoff 不動、無 combo、唔掂 S117 masking**。已 commit+push（`84033b1`）；**post-deploy smoke 確認 cpd route 生產 live（q=CPD → {sag:3,g06:3,role_facts_hr:2}、SAG quota cap=3）**。§2 rule 6 override 已記（HIGH-risk 在 Leonard standing 授權 + agent-team 四重控制 + live-verify 下進行）。S118 已 closeout（Leonard「收工」2026-05-19）；Stage-2 goal-A closed-as-non-viable。

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
- PASS 生產 deploy：post-deploy smoke 確認 cpd route live（`/api/search/channel-b` q=CPD → source_ids {sag_2025_11:3,g06:3,role_facts_hr:2}、SAG quota cap=3、未 degraded）。PENDING（待 Leonard）：probes=8-live INSPECT 未跑；Supabase `57014` timeout 未處理；CB-3 未做；Stage 2 combo＝closed（非 pending）。

Post-startup first action: 完成 §1 起手序 + HANDOFF_PACKAGE + 自測（git HEAD 應 ≥ `84033b1` / stats / egress 實測）後，**PLAN-1b 4 route 已 promote+verified+生產確認（post-deploy smoke：cpd route live、SAG cap=3）——第一件事＝問 Leonard 排序**：(a) 跑唯讀 probes=8-live INSPECT（SQL 已備）(b) Supabase free-tier probes=8 `57014` timeout 生產可用性 (c) 病假 combo-gap future PLAN-1c vs 接受 fixed-only / 抑或推進 CB-3（北極星頁數）。**未 Leonard 明示前唔好自行做 Stage 2（已 closed-as-non-viable，勿復活）/ 其他 Draft / CB-3**。碰 admin/auth/公開推送前必讀 §E.10。Channel B 北極星見 memory project_direction_review；Stage-2-vs-PLAN-1b lever 見 memory project_cb_retrieval_lever。詳細 grade/audit/live-verify 證據喺 Testing/poc-retrieval/eval/PLAN1B_grade_report.md + CB2_STAGE2_grade_report.md。
```

---
