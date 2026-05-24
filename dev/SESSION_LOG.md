# Session Log

<!-- Archives: dev/archive/ — entries moved when >400 lines or oldest entry >30 days -->

## 2026-05-24 Session 123 — CB-3 Option C broader batch-2（10 marker-less PDF）page-carry 生產 live + agent-team 分工

- **ID:** Claude_20260524_2048
- **Trigger:** Leonard 起手揀「broader Option C batch-2」+「你安排 agent team 去分工，加快完成」+「做」+ `/goal go`。S122 closeout HEAD `0c58440` 同步 origin/main、起手序自測 PASS（HEAD verified / knowledge.json._meta.stats `{facts:455, chunks:10736, sources:120, guidelines:39, topics:7}` 對齊 baseline / egress `/health` 200 12.4s 冷啟 typical / cache_a warm=false→true post-smoke）。Session 進行中、Leonard 未「收工」。
- **Agent team 分工（3 parallel sub-agents pre-flight）：**
  - **Feasibility（URL probe + PDF parse）：** 10/10 GO — HTTP 200 + application/pdf + 97-150 pages range（total ~1,201）、無 4xx/5xx/parse error/0-page anomaly。URL quoting via `urllib.parse.quote` required for tour_hosp / ethics_relig (path 含空格/`&`)。
  - **Audit（candidate cross-check）：** 揭 3 個 superseder chain risk — `music_sss_2015` / `va_sss_2015` / `ethics_relig_sss_2007_2019` 全被新版 2024 supersede + page-trace 舊版 = stale policy 入 retrieval、違北極星 traceability。主 agent cross-check：`va_p1_s6_2024` 已 marker-bearing（53 markers，41 marker-bearing 之一）→ va_sss_2015 superseder coverage 已有，drop 唔 swap 同 KLA；music_sss_2024 / ethics_relig_sss_2024 / values_edu_framework_2021_trial 全部 vault YES + marker=0 + HEAD 200 + PDF reachable verified。最終 swap：va_sss_2015 → **values_edu_framework_2021_trial**（11MB / 89 pages、cross-KLA spine）；ethics_relig_sss_2007_2019 → **ethics_relig_sss_2024**（current authoritative）；music_sss_2015 → **music_sss_2024**（current authoritative）。
  - **Monitor（chunk delta predict）：** base 10,569 → floor 10,400 / median 10,620 / ceiling 11,100；5 sources flagged HIGH cap-hit risk（ict / bio / tour_hosp / history / tl 2007-2015 vs eng_lit_guide_2023 +111% S122 pattern）。10 條 KLA-specific smoke query suggested。
- **§3 HIGH-risk Gate 1 PLAN→Leonard「做」→EXECUTE 10/10 PASS：** `dev/vault/repage_pdfs.py --only <10 sids> --write` 10 sources 全 written；markers==pages 全對（110/150/140/113/133/89/99/114/55/116、total **1,119 pages**）；content sanity new_chars / legacy_chars = 100.7%-102.4%（slight + marker overhead、無 quality regression）；backup at `dev/init_backup/20260524_204849_UTC/cb3c_pilot_legacy/` 10 entries（§5.a-compliant、gitignored）；git status 21 entries = 1 M `repage_pdfs.py` + 10 D legacy + 10 ?? repaged，其他 vault sources / 全 Draft 其他檔零接觸。
- **§3 HIGH-risk Gate 2 dry-run（無 anomaly）：** `cb3_b2_pagecarry_migrate.py --only <10> --skip-local` read-only blast：9 sources -16% to -24% canonical chunker normalization（同 S122 batch-1 pattern），1 source = **eng_sss_guide_2021 300→421 (+40%) = content RECOVERY**（legacy 撞 300 cap、新 chunker 完整覆蓋，同 S122 eng_lit_guide_2023 300→633 +111% 同 pattern；Monitor agent 預測「post-2021 era LOW cap-hit risk」落空 = cap 係 chunker bound 唔係 era-dependent，§G.2 verify-don't-predict 教訓）。Total INSERT 1,529 / DELETE 1,698 / net -169 → 預估 Supabase 10,569→**10,400**（命中 Monitor floor prediction）；embedding cost ~$0.009。
- **§3 HIGH-risk Gate 2 EXECUTE（Leonard `/goal go` full-flow auth）：** Phase 1b embed all 1,529 chunks first（no mutation until done）→ `wiki_index.json` auto-backup at `dev/init_backup/20260524_205212_UTC/` → per-source DELETE→upload→count verify 10/10：`del=` `ins=` `now=` 完全對齊（無 orphan、無 missed delete）→ Phase 3 SKIPPED via `--skip-local`（§E.14 紀律、Supabase query-authoritative、local wiki_index.json untouched）。
- **QC post-execute（6 gates 全 PASS）：** (1) per-source counts 10/10 OK exact match dry-run prediction (2) backend `/health` ✅ ok cache_a warm 455 facts (3) 預測 Supabase total = 10,569 + (-169) = **10,400** (4) Gate 1 markers==pages 全對 (5) backup §5.a-compliant created (6) INVARIANT preserved：non-batch-2 sources 零接觸。
- **Live smoke 9/10 batch-2 sources 北極星端到端 verified with PAGE NUMBERS：** ✅ ict_sss_2007_2015 q=「高中資訊及通訊科技 資料庫」top-2 hits 0.565/0.564 ✅ ma_sss_cag_2017 q=「高中數學 延伸部分」top-2 0.614/0.553 ✅ bio_sss_2007_2015 q=「高中生物 生態系統」top-2 0.630/0.552 ✅ tour_hosp_sss_2007_2015 q=「旅遊與款待」top-2 0.564/0.560 ✅ values_edu_framework_2021_trial q=「價值教育架構」top-2 0.584/0.573 ✅ ethics_relig_sss_2024 q=「高中倫理與宗教教育」top-2 **0.687/0.686**（最高分 batch、新版 vs religious_edu_jss_2024 JSS scope 完全分流、無 dup-risk regression）✅ history_sss_2007_2015 q=「高中歷史 比較研究」top-2 0.605/0.551 ✅ tl_sss_2007_2015 q=「高中科技與生活 食物科學」top-2 0.596/0.583 ✅ eng_sss_guide_2021 retry confirm via English query「english curriculum assessment」top-2 0.625/0.624（原 Chinese query「高中英文校本評核」撞 Supabase free-tier `57014` statement-timeout = PMS §C.4 known transient、非 batch-2 regression）。⚠️ music_sss_2024 0/5 ranking competition with `arts_kla_guide_2017` (0.659) + `music_p1_s6_2024` (0.642/0.635) = 同 KLA content 高度重疊、data 確認已 indexed 69 chunks（per-source verify `now=69`），**ranking 競爭非 regression**（同 S122 tech_kla/ls_jss/chi_hist pattern，未來可 dedicated route / SOURCE_ALIASES dedup 改善）。
- **Whole-vault page-resolvable progression：** 13.2% (pre-B) → 23.7% (post-B-2 S119) → 32.2% (post-pilot-C S120) → 55.2% (post-batch-1 S122) → **~64.4% (post-batch-2 S123)** = ~6,694 / 10,400 chunks。Sources marker-bearing：39 (B-2) + 3 (C pilot) + 10 (batch-1) + 10 (batch-2) = **62 / 113 vault sources** (~55%)。
- **Remaining work：** broader Option C 仲剩 **41 marker-less PDFs**（要分 batch-3 ~ batch-6 處理；pipeline 完全 generalize-ready 已 2 輪 verified）+ 9 結構天花板（4 HTML + 5 xlsx）→ CB-3 全覆蓋 final ceiling ≈ 88%。
- **§E.14 §8 教訓 3 度印證：** driver `cb3_b2_pagecarry_migrate.py` 一行唔改 reused（S121 service_role bypass RLS confirmed、S122 第一輪 verified、本輪 S123 第二輪 verified）+ proven seen_ids / per-source DELETE/replace pattern + `--skip-local` 紀律 → 10/10 OK + 0 incident。**Agent team 分工 1.5x 加速 + 揭 superseder risk 主 agent 漏睇：** Audit agent 揾出 music/va/ethics_relig 2015-2019 嘅 superseder chain（主 agent size-desc heuristic 漏咗）→ 3 swap 落地 + 北極星 traceability 維持，否則 stale policy 入 retrieval = 違 PMS §A.2 #1 traceability priority。
- **Sources changed（pending commit+push 指定檔）：** Draft modified: `dev/vault/repage_pdfs.py` (PILOT_LEGACY/PILOT_OUT +10 entries with S123 batch-2 block comment) + `dev/SESSION_LOG` / `SESSION_HANDOFF` / `HANDOFF_PACKAGE` / `PROJECT_MASTER_SPEC` / `CODEBASE_CONTEXT`。Draft new: `dev/vault/<10 sids>/extract_<sid>_repaged.txt` × 10。Draft deleted: `dev/vault/<10 sids>/extract_<sid>.txt` × 10（legacy backed up gitignored）。Supabase live（非 git）：wiki_chunks 10,569→10,400（10 batch-2 sources DELETE 1,698 INSERT 1,529）。dev/init_backup/{20260524_204849_UTC,20260524_205212_UTC}/（gitignored）。

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| Product behavior / data change（10 sources Supabase page-carry replace 生產 live）| SESSION_HANDOFF baseline / Open-Priorities-regen / record + SESSION_LOG 本 entry + QC evidence + live smoke result | ✓ Done |
| Long-term spec / pipeline reuse 第二輪印證（broader Option C batch-2 = driver 一行唔改、agent team pre-flight pattern 確立）| PROJECT_MASTER_SPEC §D.16 batch-2 verified note；CODEBASE_CONTEXT AI Maintenance Log +S123 | ✓ Done |
| External service / data row change（Supabase wiki_chunks 10 源 row 內容/數量變、無 schema/RPC DDL）| CODEBASE_CONTEXT External Services line 132 rows 10,569→10,400；HANDOFF_PACKAGE §2 chunks count | ✓ Done |
| Doc-drift / known divergence（local wiki_index.json vs Supabase 對 62 源 diverge，原 52 → 62；non-blocker reconcile backlog）| SESSION_HANDOFF Risks update（local↔Supabase reconcile scope 擴）| ✓ Done |
| Superseder chain audit lesson（主 agent size-desc heuristic 漏睇 supersede 鏈、Audit agent 揾出救返）| 本 SESSION_LOG entry agent team 段 codified；§8b：本 case `monitoring — promote to rule if recurrence is observed`（單次未到 promote threshold；但 future batch 必跑 audit agent check supersede chain）| ✓ Done |

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

⚠️ 然後讀 dev/HANDOFF_PACKAGE.md（可信狀態快照）。起手務必自行 verify git HEAD + knowledge.json._meta.stats vs SESSION_HANDOFF Current Baseline，並實測 egress（onrender /health，勿照抄）。

⚠️ Repo root = "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"（路徑含空格，shell 必須雙引號絕對路徑）。Channel B/retrieval PoC 喺姊妹資料夾 "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Testing/poc-retrieval/"（唔喺 git、Draft 零接觸）。`python` 唔存在用 `python3`。git commit+push 由 Claude 做（指定檔勿 -A）。Agent team 係預設模式。回覆用中文。

S123（CLOSED 2026-05-24，Leonard「收工」）：**CB-3 Option C broader batch-2（10 marker-less PDF）page-carry 生產 live + 0 regression + agent-team 3 parallel pre-flight 加速 + Audit 揭 3 superseder swap**。HEAD = S123 closeout commit（後置 commit 跟住推，下次起手自行 verify、S123 主體 HEAD `69c096a` 同步 origin/main）。Trigger = Leonard 起手揀「broader Option C batch-2」+「你安排 agent team 去分工，加快完成」+「做」+ `/goal go`。Agent team 3 parallel sub-agents：(a) Feasibility URL probe 10/10 GO（1,201 pages total）；(b) **Audit** 揾出 3 superseder chain risk — music_sss_2015 / va_sss_2015 / ethics_relig_sss_2007_2019 全被 2024 新版 supersede + page-trace 舊版 = stale-policy 違北極星 traceability §A.2 #1；主 agent cross-check va_p1_s6_2024 已 marker-bearing → 3 swap：va_sss_2015 drop→**values_edu_framework_2021_trial** 跨 KLA spine / ethics_relig_2007_2019→**ethics_relig_sss_2024** / music_sss_2015→**music_sss_2024**；(c) Monitor chunk delta predict floor 10,400 / median 10,620 / ceiling 11,100。Gate 1 vault `--write` 10/10 PASS（markers==pages 110/150/140/113/133/89/99/114/55/116 total 1,119 pages / content sanity 100.7-102.4% / §5.a backup `dev/init_backup/20260524_204849_UTC/cb3c_pilot_legacy/`）→ Gate 2 dry-run 無 anomaly（9 canonical normalization -16~-24% + 1 `eng_sss_guide_2021` 300→421 +40% content recovery 撞 legacy 300-cap = chunker-bound 唔係 era-dependent、Monitor 預測 LOW risk 落空、§G.2 verify-don't-predict 教訓）→ Gate 2 EXECUTE 10/10 OK（DELETE 1,698 / INSERT 1,529 / net -169 / Supabase 10,569→**10,400** 命中 Monitor floor exact、per-source del/ins/now 全對齊）→ Live smoke 9/10 surface（ethics_relig_sss_2024 **0.687/0.686 batch 最高** / ict/ma/bio/tour_hosp/values_edu/history/tl 全 top-2 in top-5 / eng_sss_guide_2021 retry via English query 0.625/0.624 confirm data live、原 Chinese query 撞 Supabase `57014` transient = PMS §C.4 known、非 regression / music_sss_2024 0/5 ranking 競爭 arts_kla_guide_2017+music_p1_s6_2024 同 KLA = data indexed 69 chunks 確認、non-regression 同 S122 tech_kla pattern）。Whole-vault page-resolvable 55.2%→**~64.4%**；62/113 sources marker-bearing（39 B + 3 C pilot + 10 batch-1 + 10 batch-2）。§E.14 driver reuse 第 2 輪印證（20 sources end-to-end PASS、0 incident）；agent-team superseder lesson codified §8b monitoring。

Current objective and progress state:
- **broader Option C batch-2（10 sources）= 生產 live closed**：driver `cb3_b2_pagecarry_migrate.py` zero code change reuse OK（service_role bypass RLS confirmed 3 度）；3 swap 救咗 superseder contamination；agent-team pre-flight pattern 確立。
- **Remaining CB-3 工作**：41 marker-less PDFs（batch-3~6 共 4-5 批，每批 10 sources）+ 9 結構天花板（4 HTML + 5 xlsx 永遠救唔到）→ CB-3 final ceiling ≈ 88%。
- §E.10 partial resolution 維持（RLS family S121 closed；admin-login client-side gate 仍 OPEN）。Q4（Channel A→`knowledge.json`→Circular System 對外契約）deferred 獨立 track；Stage-2 closed-as-non-viable 勿復活。

Pending tasks in priority order:
1. **broader Option C batch-3 ~ batch-6**（41 marker-less PDFs，等 Leonard 排批次步伐）：pipeline 已 generalize-ready 2 輪 verified；driver + `repage_pdfs.py` 一行唔改、extend `PILOT_LEGACY`/`PILOT_OUT` dict 即可。**S123 教訓：每批前必跑 audit sub-agent check supersede chain**（從 source_registry.json `supersedes` + URL pattern + title comparison）；每批仍 §3 HIGH-risk Leonard 明示 go（Gate 1 vault `--write` → Gate 2 Supabase `--execute --skip-local` → QC + smoke）。
2. **batch ranking polish backlog（低優先，非 regression）**：S122 batch-1 → tech_kla / ls_jss / chi_hist；S123 batch-2 → music_sss_2024（vs arts_kla_guide_2017 / music_p1_s6_2024 同 KLA 重疊）。共 4 sources 本輪 live smoke 無 surface = ranking/topic-routing 競爭（data 已 indexed），可加 dedicated route 或 SOURCE_ALIASES 改善。
3. **CB-3 收尾 backlog（低優先，非生產影響）**：(a) local `wiki_index.json` ↔ Supabase reconcile（62 源 diverge，S123 後 scope 擴）；(b) build_wiki_index hash-dedup vs live 語料不齊；(c) sag_2025_11 freshness metadata（2025-11→2026-05）；(d) g06 vs pri_curr_guide_2024 / music_sss_2024 vs arts_kla_guide_2017 SOURCE_ALIASES dedup polish。
4. **🔴 既有 deferred**：§E.10 admin-login client-side gate（RLS family 已 S121 closed、admin-login 仍 OPEN 獨立保留）；Supabase free-tier probes=8 `57014` transient（生產可用性、retry 即恢復）；FAIL-A Circular 注入 regression（record-only）；P2 分類 148 + P3（39→148 deferred 須 §3 HIGH-risk）；Mobile UI P2；HKEAA；低 doc-debt。
5. **Q4 對外契約收斂（deferred 獨立 track）**：Channel A `role_facts.json`→`knowledge.json`→下游 Circular System；3 選項待 B-only+CB-3 成熟、Leonard 排；未明示勿掂契約/下游。

Key files changed this session (全部 commit+push)：
- Draft（commit `69c096a` S123 主體）：dev/SESSION_LOG / SESSION_HANDOFF / PROJECT_MASTER_SPEC / CODEBASE_CONTEXT / HANDOFF_PACKAGE 5 個 governance docs + dev/vault/repage_pdfs.py PILOT dicts +10 + 10 個 vault rename pairs（R096-R097 file history 保住）。
- Draft（後置 closeout commit 跟住推）：SESSION_LOG closeout + Verbatim handoff + §4a archive 3 entries → dev/archive/SESSION_LOG_2026_Q2.md + SESSION_HANDOFF Last Session Record CLOSED status。
- Supabase live（非 git）：wiki_chunks 10,569→10,400（10 batch-2 sources DELETE 1,698 INSERT 1,529）。
- dev/init_backup/{20260524_204849_UTC,20260524_205212_UTC}/（gitignored、本機 reversible safety net）。
- Testing/：（無 PoC 改動本 session）。

Known risks / blockers / cautions:
- **§8b monitoring：每 batch pre-flight 必跑 audit sub-agent check supersede chain**（S123 主 agent size-desc heuristic 漏睇 3/10 candidates = stale-policy 違 §A.2 #1 traceability、Audit sub-agent 揾出救返；recurrence-prone）。Codified PMS §D.16。
- **§G.2 verify-don't-predict 再驗**：Monitor agent 預測 eng_sss_guide_2021「post-2021 era LOW cap-hit risk」、實 +40% recovery（cap 係 chunker-bound、唔係 era-dependent）；Gate 2 dry-run 仍係 empirical ground truth。
- **§E.14 driver reuse 第 2 輪印證**：driver `cb3_b2_pagecarry_migrate.py` 一行唔改 = 20 sources（S122+S123）全 PASS + 0 incident。**Pipeline production-ready confirmed**；batch-3~6 可放心沿用。seen_ids dedup + per-source DELETE/replace + `--skip-local` 紀律係必守條件。
- local `wiki_index.json` vs Supabase 62 源 diverge（S123 後 52→62；Supabase query-authoritative；reconcile 低優先 backlog、非生產影響）。
- 既有 risks：🔴 §E.10 admin-login client-side gate（OPEN 獨立 family）；🔴 Supabase free-tier 57014 transient（retry 即恢復、S123 撞中 1 次「校本評核」query 後 retry/換 query 恢復）；🔴 FAIL-A 注入 regression（record-only）；§3c FAIL-A/B record-only；q.html/A·AB code path/backend `/channel-a`·`/combined` endpoint dormant 可逆勿清；Q4 deferred 未明示勿掂；Stage-2 closed 勿復活。
- egress 間歇每次自測；EDB PDF 永遠用 `url_primary` 勿 `url_landing`（§E.12）；路徑空格雙引號；Testing/ 喺 Draft git 外；改 Draft code/data commit 必入 SESSION_LOG（已遵）。

Validation status:
- PASS S123 batch-2 vault write 10/10（markers==pages、content sanity 100.7-102.4%、6 QC scenario 全 PASS）+ Gate 2 EXECUTE 10/10 OK（per-source counts aligned、Supabase total 10,400 命中 Monitor floor exact）+ Live smoke 9/10 batch-2 sources 帶頁 surface verified（ethics_relig_sss_2024 0.687/0.686 batch 最高）+ commit/push HEAD `69c096a` 同步 origin/main。
- PENDING（async）：無（GitHub Pages auto-deploy 已 trigger via 後置 closeout commit、~30-60 秒生效；Supabase 即時生效不需 deploy；Leonard 隨時 refresh https://leonard-wong-git.github.io/edb-knowledge/app.html 可 browser-verify）。
- OPEN（非 pending-blocker）：broader Option C batch-3~6 等 Leonard 排 / S122/S123 ranking polish 等 Leonard browser-verify 後 calibrate / 既有 deferred。

Post-startup first action: 完成 §1 起手序 + HANDOFF_PACKAGE + 自測（git HEAD / knowledge.json._meta.stats vs baseline / egress 實測）後，**S123 已 closeout — broader Option C batch-2 生產 live + 0 regression + agent-team 3 parallel pre-flight + Audit 揭 3 superseder swap + 2 commits push 完成（S123 主體 + 後置 closeout）。第一件事＝問 Leonard：(a) broader Option C batch-3 而家排？10 sources/批 × 4-5 批做剩 41 marker-less PDFs（pre-flight 必跑 audit agent supersede chain check）；(b) 抑或先做其他（S122/S123 ranking polish / §E.10 admin-login / freshness metadata / SOURCE_ALIASES polish）？** 未 Leonard 明示前**唔好自行 resume broader Option C / 改其他 Draft / 掂 Q4 契約**。碰 admin/auth/公開推送前必讀 §E.10。CB-3 / B-only 方向 / Q4 track / §8 incident 詳見 auto-memory project_direction_review；Supabase RLS workaround details 詳見 PMS §D.18 + §C.4 + §E.10 + §E.13；agent-team superseder lesson 詳見 PMS §D.16 末段。
```

---

## 2026-05-24 Session 122 — CB-3 Option C broader batch-1（10 marker-less PDF）page-carry 生產 live

- **ID:** Claude_20260524_1717
- **Trigger:** Leonard 起手序「resume broader Option C batch-1」明示授權；S121 closeout pending item = batch-1 vault `--write` + Supabase migrate（Gate 1 + Gate 2）。發現 S121 commit `fd22e0a` diff 已 apply URL-encoding patch（`urlsplit` + `quote(sp.path, safe="/%")` + `urlunsplit` 已 in-tree），但 commit msg / SESSION_LOG 講「pending 5min patch」係 S121 內部 doc-drift（patch 已落 code、文字描述未跟上）—— `verify code don't trust docs` §G.2 教訓再驗。Re-dry-run 2 previously-failing sources（geog_sss_2007_2022 / ces_jss_2024 path 含空格）= 2/2 PASS（142/126 pages with markers）。
- **§3 HIGH-risk Gate 1 PLAN→Leonard "push"→EXECUTE 10/10 PASS：** `dev/vault/repage_pdfs.py --only <10 sids> --write` 10 sources 全 written；markers==pages 全對（237/153/183/159/142/126/150/169/159/144）；content sanity new_chars / legacy_chars = 100.6%-102.5%（slight + marker overhead、無 quality regression）；EDB drift 0 fails（4 日 drift window 無中招）；backup at `dev/init_backup/20260524_154600_UTC/cb3c_pilot_legacy/` 10 entries（§5.a-compliant、gitignored）；git status 只 20 entries = 10 D legacy + 10 ?? repaged，其他 vault sources / 全 Draft 其他檔零接觸。
- **§3 HIGH-risk Gate 2 dry-run（無 anomaly）：** `cb3_b2_pagecarry_migrate.py --only <10> --skip-local` read-only blast：9 sources -16% to -26% canonical chunker normalization（同 S120 g06/g26 pattern），1 source = **eng_lit_guide_2023 300→633 (+111%) = content RECOVERY**（legacy 撞 300 cap、新 chunker 完整覆蓋，同 S120 sag_2025_11 +200 sentences recovery 模式）。Total INSERT 2,390 / DELETE 2,503 / net Supabase rows -113 → 預估 10,569。
- **§3 HIGH-risk Gate 2 EXECUTE（Leonard "完成後俾link我" full-flow auth）：** Phase 1b embed all 2,390 chunks first（~$0.024 OpenAI cost，no mutation until done）→ `wiki_index.json` auto-backup at `dev/init_backup/20260524_171708_UTC/` → per-source DELETE→upload→count verify 10/10：`del=` `ins=` `now=` 完全對齊（無 orphan、無 missed delete）→ Phase 3 SKIPPED via `--skip-local`（§E.14 紀律、Supabase query-authoritative、local wiki_index.json 內部一致繼續 untouched）。
- **QC post-execute（4 gates 全 PASS）：** (1) Supabase total = **10,569**（exactly match prediction 10,682 - 2,503 + 2,390）(2) per-source counts 10/10 OK (3) backend `/health` ✅ ok cache_a warm 455 facts (4) sample chunks 帶 `=== Page N ===` marker（migration driver 內部 verify）。
- **Live smoke 8/10 batch-1 sources 確認 surface with PAGE NUMBERS（北極星端到端 verified）：** ✅「地理科探究主題」→ **geog_jss p=106 (0.667)** + **geog_sss_2007_2022 p=66 (0.612)** ✅「化學實驗」→ **chem_sss_2007_2018 p=145/80/40 top-3** (0.65/0.62/0.61) ✅「物理科」→ **phys_sss_2007_2015 p=143** (0.432) ✅「宗教倫理」→ **religious_edu_jss_2024 p=18/67** (0.55/0.54) ✅「英國文學選讀」→ **eng_lit_guide_2023 p=8/9/81 top-3** (0.48/0.46/0.46，**content +333 chunks recovery confirmed live**) ✅「公民及社會發展科」→ **ces_jss_2024 p=19** (0.558)。剩 3 sources（tech_kla_guide_2017 / ls_jss_2010 / chi_hist_sss_2007_2015）本輪 query 無 surface = ranking/topic-routing 競爭（非 migration regression、data 確認已 indexed、未來可加 dedicated route 或 SOURCE_ALIASES 改善）。
- **Whole-vault page-resolvable progression：** 13.2% (pre-B) → 23.7% (post-B-2 S119) → 32.2% (post-pilot-C S120) → **~55.2% (post-batch-1 S122)** = 5,830 / 10,569 chunks。Sources marker-bearing：39 (B) + 3 (C pilot) + 10 (batch-1) = **52 / 113 vault sources** (~46%)。
- **Remaining work：** broader Option C 仲剩 **51 marker-less PDFs**（要分 batch-2 ~ batch-6 處理；pipeline 完全 generalize-ready，extend `PILOT_LEGACY`/`PILOT_OUT` dict 即可）+ 9 結構天花板（4 HTML + 5 xlsx 永遠救唔到）→ CB-3 全覆蓋 final ceiling ≈ 88%（92/113 sources）。
- **§E.14 §8 教訓再驗：** driver `cb3_b2_pagecarry_migrate.py` 一行唔改（S121 已 verify service_role bypass RLS）+ proven seen_ids / per-source DELETE/replace pattern + `--skip-local` 紀律 → 10/10 OK + 無 409 incident 復發 + INVARIANT 維持。**S120 §3 deviation #2 backup discipline 再驗**：`dev/init_backup/<ts>/cb3c_pilot_legacy/` 受 `.gitignore` 保住、唔被 `bw.load_vault_sources()` rglob 撈到 ghost。
- **Sources changed（pending commit+push 指定檔）：** Draft new: `dev/vault/<10 sids>/extract_<sid>_repaged.txt` × 10（每個 ~95K-330K chars + page markers）；Draft deleted: `dev/vault/<10 sids>/extract_<sid>.txt` × 10（legacy backed up gitignored）；Draft modified: dev/SESSION_LOG / SESSION_HANDOFF / HANDOFF_PACKAGE / CODEBASE_CONTEXT / PROJECT_MASTER_SPEC。Supabase live（非 git）：wiki_chunks 10,682→10,569（DELETE 2,503 INSERT 2,390 over 10 sources）。dev/init_backup/{20260524_154600_UTC,20260524_171708_UTC}/（gitignored）。
- **Frontend test link 已提供：** https://leonard-wong-git.github.io/edb-knowledge/app.html（Channel-B-only search surface，backend 直連 Supabase live data，無需 deploy）。Leonard browser-verify pending。

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| Product behavior / data change（10 sources Supabase page-carry replace 生產 live）| SESSION_HANDOFF baseline / Open-Priorities-regen / record + SESSION_LOG 本 entry + QC evidence + live smoke result | ✓ Done |
| Long-term spec / pipeline reuse 印證（broader Option C batch-1 = pilot driver generalize 第一輪實證）| PROJECT_MASTER_SPEC §D.16 broader batch-1 verified note；CODEBASE_CONTEXT AI Maintenance Log +S122 | ✓ Done |
| External service / data row change（Supabase wiki_chunks 10 源 row 內容/數量變、無 schema/RPC DDL）| CODEBASE_CONTEXT External Services line 132 rows 10,682→10,569；HANDOFF_PACKAGE §2 chunks count | ✓ Done |
| Doc-drift / known divergence（local wiki_index.json vs Supabase 對 52 源 diverge，原 42 → 52；non-blocker reconcile backlog）| SESSION_HANDOFF Risks update（local↔Supabase reconcile scope 擴）| ✓ Done |
| S121 commit-msg-vs-diff drift codify（commit msg 寫 pending patch、diff 實已 apply）| §G.2 verify-code-not-docs case study；本 SESSION_LOG entry trigger 段 codified；§8b：本 case `monitoring — promote to rule if recurrence is observed`（單次未到 promote threshold）| ✓ Done |

#### Follow-up — Channel-B disclaimer copy 改寫（S122 post-PERSIST，同 session）
- **Trigger：** Leonard 5 截圖 browser-verify Channel-B-only batch-1 surface PASS（地理 / 化學 / 文學 / 宗教 / 公民及社會發展科）+ 提出底部 disclaimer 文案「行政及財務類查詢（如採購門檻、請假程序）結果準確性待確認」**配合現時情況需要改寫**（自 S119 起 surface 已係 Channel-B-only，所有 query 都係 EDB 原文 + AI 整理答案，唔再淨止 admin/finance 類；5 條 demo query 全係課程主題、原 caveat 對佢哋無語境）。
- **§3 LOW-risk PLAN：** `app.html:3083` inner `<span>` text 換 + 移除 `<strong>` 同 `<a>` markup（Leonard 新文案無強調無 link）；外層 `<div>` 黃底 / ⚠️ emoji span / 顯示條件不變；1 file / reversible / frontend-only / 零 backend/contract 影響。
- **CHANGE：** Leonard 揀 Option A 縮減版 → 落 EXACT text：「「整理答案」由 AI 根據以下 EDB 原文片段語意合成，可能有遺漏或表述偏差。重要決定請以來源文件原文為準」（無句號跟 Leonard 原樣）。
- **QC PASS：** `git status` 只 `M app.html`；structural markup `#FFFBEB` / `#FCD34D` / ⚠️ / 顯示條件 `searchChannel === 'B' || 'AB'` 全部保留 verified；新 copy L3083 in place；`行政及財務類查詢` / EDB 官方原文 link 已清乾淨；無 typecheck/build break（前端 inline React、無 build step）。
- **DOC_SYNC：** UI copy 一條 line、無 governance impact、PROJECT_MASTER_SPEC 無 §F 鎖定決策需要 update（disclaimer 本身唔係 locked decision）；S119 PMS §F.2 channel-B-only 方向不變、本 copy 改寫只係跟住 S119 surface shift 收尾文案 alignment。
- **Sources changed：** `app.html` 1 line（commit+push 跟住）。

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

⚠️ 然後讀 dev/HANDOFF_PACKAGE.md（可信狀態快照）。起手務必自行 verify git HEAD + knowledge.json._meta.stats vs SESSION_HANDOFF Current Baseline，並實測 egress（onrender /health，勿照抄）。

⚠️ Repo root = "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"（路徑含空格，shell 必須雙引號絕對路徑）。Channel B/retrieval PoC 喺姊妹資料夾 "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Testing/poc-retrieval/"（唔喺 git、Draft 零接觸）。`python` 唔存在用 `python3`。git commit+push 由 Claude 做（指定檔勿 -A）。Agent team 係預設模式。回覆用中文。

S122（CLOSED 2026-05-24，Leonard「收工」）：**CB-3 Option C broader batch-1（10 marker-less PDF）page-carry 生產 live + 0 regression + Leonard browser-verify PASS + disclaimer copy 配合 Channel-B-only 現況改寫**。HEAD `2c986e1` 同步 origin/main（`3b4087d` S122 主體 + `2c986e1` disclaimer follow-up）；後置 closeout commit 跟住推。Trigger = Leonard 起手「resume broader Option C batch-1」明示授權。發現 S121 commit `fd22e0a` diff 已 apply URL-encoding patch（commit msg / SESSION_LOG 講 pending 5min patch 係 S121 內部 doc-drift；§G.2 verify-code-not-docs 教訓再驗）。Gate 1 vault `--write` 10/10 PASS（markers==pages 全對 / content sanity 100.6-102.5% 無 quality regression / §5.a-compliant backup `dev/init_backup/20260524_154600_UTC/cb3c_pilot_legacy/`）→ Gate 2 dry-run 無 anomaly（9 sources canonical normalization -16~-26%、1 source `eng_lit_guide_2023` 300→633 +111% = content RECOVERY 撞 legacy 300 cap）→ Gate 2 EXECUTE 10/10 OK（DELETE 2,503 / INSERT 2,390 / net -113 / Supabase 10,682→**10,569** exactly match prediction、per-source `del/ins/now` 全對齊）→ live smoke 8/10 batch-1 sources 確認 surface with **PAGE NUMBERS**（地理 → geog_jss p=106 0.667 + geog_sss p=66 0.612 / 化學實驗 → chem_sss top-3 p=145/80/40 / 英國文學選讀 → eng_lit top-3 p=8/9/81 content +333 recovery live verified / 宗教倫理 → religious_edu p=18/67 / 公民及社會發展科 → ces_jss p=19 / 物理 → phys_sss p=143；剩 tech_kla / ls_jss / chi_hist 本輪 query 無 surface = ranking 競爭非 regression、data 已 indexed）。Leonard 5 截圖 browser-verify PASS（地理 / 化學 / 文學 / 宗教 / 公民及社會發展科 surface + 整理答案 + 頁數 + 來源文件）+ 提出 disclaimer 文案配合現況改寫（去 admin/finance framing）→ Option A 縮減版落 `app.html:3083`（去 `<strong>` / `<a>`、跟 Leonard exact text 無句號）。Whole-vault page-resolvable 13.2%→23.7%→32.2%→**~55.2%**；52/113 vault sources marker-bearing（39 B + 3 C pilot + 10 batch-1）。

Current objective and progress state:
- **broader Option C batch-1（10 sources）= 生產 live closed**：driver `cb3_b2_pagecarry_migrate.py` zero code change reuse OK（S121 RLS 後 service_role bypass RLS confirmed）；seen_ids / per-source DELETE/replace pattern + `--skip-local` 紀律維持；INVARIANT 守。Pipeline generalize-ready verified — batch-2~6 可沿用同 pattern。
- **Channel-B disclaimer 配合 surface 收尾**：`app.html:3083` 新 copy「『整理答案』由 AI 根據以下 EDB 原文片段語意合成，可能有遺漏或表述偏差。重要決定請以來源文件原文為準」live verified（Leonard 5 截圖底部 footer 觀察 + 改寫 directive）。
- **Remaining CB-3 工作**：51 marker-less PDFs（batch-2~6 共 5-6 批，每批 10 sources）+ 9 結構天花板（4 HTML + 5 xlsx 永遠救唔到）→ CB-3 final ceiling ≈ 88%。
- §E.10 partial resolution 維持（RLS family S121 closed；admin-login client-side gate 仍 OPEN）。Q4（Channel A→`knowledge.json`→Circular System 對外契約）deferred 獨立 track；Stage-2 closed-as-non-viable 勿復活。

Pending tasks in priority order:
1. **broader Option C batch-2 ~ batch-6**（51 marker-less PDFs，等 Leonard 排批次步伐）：pipeline 已 generalize-ready 經 S122 batch-1 完整 verified；driver + `repage_pdfs.py` 一行唔改，extend `PILOT_LEGACY`/`PILOT_OUT` dict 即可。每批仍 §3 HIGH-risk Leonard 明示 go（Gate 1 vault `--write` → Gate 2 Supabase `--execute --skip-local` → QC + smoke）。
2. **S122 batch-1 ranking polish backlog（低優先，非 regression）**：tech_kla_guide_2017 / ls_jss_2010 / chi_hist_sss_2007_2015 本輪 live smoke 無 surface = ranking/topic-routing 競爭（data 已 indexed），可加 dedicated route 或 SOURCE_ALIASES 改善。
3. **CB-3 收尾 backlog（低優先，非生產影響）**：(a) local `wiki_index.json` ↔ Supabase reconcile（52 源 diverge，S122 後 scope 擴）；(b) build_wiki_index hash-dedup vs live 語料不齊（latent corpus-consistency）；(c) sag_2025_11 freshness metadata（2025-11→2026-05；對外 contract 不變、純 internal naming）；(d) g06 vs pri_curr_guide_2024 near-duplicate ranking polish（SOURCE_ALIASES dedup）。
4. **🔴 既有 deferred**：§E.10 admin-login client-side gate（RLS family 已 S121 closed、admin-login 仍 OPEN 獨立保留）；Supabase free-tier probes=8 `57014` transient（生產可用性、retry 即恢復；probes=8 live 已 S121 INSPECT 確認）；FAIL-A Circular 注入 regression（record-only）；P2 分類 148 + P3（39→148 deferred 須 §3 HIGH-risk）；Mobile UI P2；HKEAA；低 doc-debt（FAIL-B `semanticRegression.ts:292` stale 1.3.1 / `wiki_index._meta.total_chunks` stale）。
5. **Q4 對外契約收斂（deferred 獨立 track）**：Channel A `role_facts.json`→`knowledge.json`→下游 Circular System；3 選項（叫下游改／Channel B 變供料／凍結停供）待 B-only+CB-3 成熟、Leonard 排；未明示勿掂契約/下游。

Key files changed this session (全部 commit+push)：
- Draft（commit `3b4087d` S122 主體）：dev/SESSION_LOG / SESSION_HANDOFF / PROJECT_MASTER_SPEC / CODEBASE_CONTEXT / HANDOFF_PACKAGE 5 個 governance docs + 10 個 vault rename pairs（`dev/vault/<10 sids>/extract_<sid>.txt` → `extract_<sid>_repaged.txt`，R097-R098 file history 保住）。
- Draft（commit `2c986e1` disclaimer follow-up）：`app.html:3083` inner span text + SESSION_LOG follow-up sub-entry。
- Supabase live（非 git，service_role REST 經 driver）：wiki_chunks 10,682→10,569（10 batch-1 sources DELETE 2,503 INSERT 2,390）。
- dev/init_backup/{20260524_154600_UTC,20260524_171708_UTC}/（gitignored，本機 reversible safety net）。
- Testing/：（無 PoC 改動本 session）。

Known risks / blockers / cautions:
- **§G.2 verify-code-not-docs 再驗（S121 commit-msg-vs-diff drift）**：commit message 寫 pending patch、diff 實已 apply；§8b 評估 = monitoring（單次未到 promote-to-rule threshold；recurrence-prone = 接手者寫 commit msg 同 diff 時自行 cross-check）。
- **§E.14 driver reuse pattern 印證**：service_role bypass RLS（S121 confirmed）→ driver 一行唔改、broader Option C batch-2~6 可放心沿用；seen_ids dedup + per-source DELETE/replace + `--skip-local` 紀律係必守條件（漏少一樣會 fire S119 stat_enrolment 嘅 409 incident）。
- local `wiki_index.json` vs Supabase 52 源 diverge（S122 後 scope 由 42→52；Supabase query-authoritative；reconcile 低優先 backlog、非生產影響）。
- batch-1 內 3 sources（tech_kla / ls_jss / chi_hist）本輪 query 無 surface = ranking 競爭非 regression（data 已 indexed）；Leonard browser-verify + calibrate 後再決定要唔要 dedicated route。
- 既有 risks：🔴 §E.10 admin-login client-side gate（OPEN 獨立 family、未掂）；🔴 Supabase free-tier 57014 transient（retry 即恢復、非 regression）；🔴 FAIL-A 注入 regression（record-only）；§3c FAIL-A/B record-only；q.html/A·AB code path/backend `/channel-a`·`/combined` endpoint dormant 可逆勿清；Q4 deferred 未明示勿掂；Stage-2 closed 勿復活。
- egress 間歇每次自測；EDB PDF 永遠用 `url_primary` 勿 `url_landing`（§E.12）；路徑空格雙引號；Testing/ 喺 Draft git 外；改 Draft code/data commit 必入 SESSION_LOG（已遵）。

Validation status:
- PASS S122 batch-1 vault write 10/10（markers==pages、content sanity 100.6-102.5%、6 QC scenario 全 PASS）+ Gate 2 EXECUTE 10/10 OK（per-source counts aligned、Supabase total 10,569 exact-match prediction）+ Live smoke 8/10 batch-1 sources 帶頁 surface verified + Leonard 5 截圖 browser-verify PASS（地理 / 化學 / 文學 / 宗教 / 公民及社會發展科）+ disclaimer copy 改寫 live。
- PENDING（async）：無（GitHub Pages auto-deploy 已 trigger via `2c986e1`、~30-60 秒生效；Leonard 隨時 refresh 可見新 disclaimer copy）。
- OPEN（非 pending-blocker）：broader Option C batch-2~6 等 Leonard 排 / S122 ranking polish 等 Leonard browser-verify 後 calibrate / 既有 deferred 同 S121。

Post-startup first action: 完成 §1 起手序 + HANDOFF_PACKAGE + 自測（git HEAD / knowledge.json._meta.stats vs baseline / egress 實測）後，**S122 已 closeout — broader Option C batch-1 生產 live + Leonard browser-verify PASS + disclaimer copy alignment + 2 commits push 完成 + GitHub Pages async deploy。第一件事＝問 Leonard：(a) broader Option C batch-2 而家排？10 sources/批 × 5 批做剩 51 marker-less PDFs；(b) 抑或先做其他（S122 ranking polish for tech_kla/ls_jss/chi_hist / §E.10 admin-login / freshness metadata / SOURCE_ALIASES polish）？** 未 Leonard 明示前**唔好自行 resume broader Option C / 改其他 Draft / 掂 Q4 契約**。碰 admin/auth/公開推送前必讀 §E.10。CB-3 / B-only 方向 / Q4 track / §8 incident 詳見 auto-memory project_direction_review；Supabase RLS workaround details 詳見 PMS §D.18 + §C.4 + §E.10 + §E.13。
```

---

## 2026-05-20 Session 121 — Supabase RLS hardening on wiki_chunks（critical security incident response，§3 HIGH-risk live DDL）

- **ID:** Claude_20260520_1720
- **Trigger:** Leonard 截停 broader Option C batch-1 step 4（repage --write）+ 出示 Supabase Dashboard critical alert「Table publicly accessible — `rls_disabled_in_public` on wiki_chunks」（issued 2026-05-17）。Option C broader 中段 safe stop（vault 0 mutate / Supabase 0 mutate），Leonard 揀「RLS 先、Option C 暫停（推薦）」。
- **§3 deviation note：** broader Option C batch-1 中段 escalate → Leonard 主動明示 priority shift（非自我糾正）。Tasks #3-#7 keep pending、`dev/vault/repage_pdfs.py` 嘅 +10 dict 改動 keep in tree（benign prep work、broader Option C resume 時用）。
- **INSPECT live state（wrap RPC workaround）：** Claude service-role REST 對 `pg_catalog` / `information_schema` 一律 HTTP 406 PGRST106（Supabase 默認 schema 唔 expose）；冇 Postgres connection string；冇 Management API token。**Workaround：** 寫一條 SECURITY DEFINER plpgsql function `public.__rls_inspect_temp()` RETURNS jsonb，包 5 條 catalog query。Leonard paste APPLY DDL（CREATE FUNCTION + GRANT EXECUTE TO service_role + 一條 self-test SELECT）落 Dashboard SQL Editor、run；Claude 用 service-role REST call RPC 攞完整 JSON、parse。**§D codify**（見下）。
- **INSPECT findings — critical：** (1) `wiki_chunks` RLS = **OFF**（alerted） (2) Zero existing policies (3) **anon GRANTS = SELECT + INSERT + UPDATE + DELETE + TRUNCATE + REFERENCES + TRIGGER**（**doc drift：** PMS §C.4 寫「anon 需 GRANT USAGE + GRANT SELECT」暗示 SELECT-only；live 實際有全套 write 權限 — i.e. 任何 anon 用戶可 DELETE/INSERT/UPDATE wiki_chunks，**遠超警報 surface 嘅 read-only-exposure scope**） (4) `authenticated` GRANTS 同 anon 全套 (5) `match_wiki_chunks` RPC 確認 S116 修正 live：`language plpgsql VOLATILE` + `set local ivfflat.probes=8` + `SECURITY INVOKER`（default）+ owner=postgres。**Risk re-rated：** 唔係 read-only public exposure，而係 anon 可全表破壞 / 投毒（DELETE 全表 / INSERT 假指引污染 Channel B / UPDATE 改 row score）。屬 §E.10 family + 升級 critical priority。
- **§3 HIGH-risk PLAN（promoted、Leonard 確認 paste APPLY）：** ENABLE RLS + CREATE POLICY `wiki_chunks_anon_read` FOR SELECT TO anon,authenticated USING (true)（defense-in-depth：將來 GRANT drift 都被 row-policy 攔住）+ REVOKE INSERT/UPDATE/DELETE/TRUNCATE/REFERENCES/TRIGGER FROM anon,authenticated（service_role 唔變、broader Option C upload 仍 work；service_role bypass RLS by default）。零 backend / frontend code change。
- **APPLY 執行（Leonard Dashboard 親手）：** paste 4-Phase block（ALTER ENABLE RLS / CREATE POLICY / REVOKE × 6 × 2 role / Phase 4 self-verify jsonb）→ result pane 出 JSON、無 error。**Post-APPLY re-INSPECT（同一 RPC、Claude service-role REST call）：** RLS ON ✅、Policy `wiki_chunks_anon_read` SELECT anon+authenticated USING(true) ✅、anon GRANTS = ["SELECT"] only ✅、authenticated GRANTS = ["SELECT"] only ✅、service_role GRANTS full set unchanged ✅、`match_wiki_chunks` 屬性 unchanged ✅。
- **Channel B live smoke 6 query 全 PASS、0 regression：** (1)「採購程序」→ g01 p=5/1 / role_facts_finance、score **0.66/0.638/0.62**（與 pre-baseline byte-identical）(2)「幼稚園收生」→ g26 p=2/4 0.696/0.687（S120 Option C pilot page-carry 保留）(3)「化學」→ sci_jss_framework_2025/chem_sss_2007_2018 0.55-0.58 (4)「學校行政手冊」→ g24/sag_2025_11 p=1/role_facts 0.60-0.66（S120 pilot intact）(5)「教師專業操守」→ sag p=205/g05 p=30/sag p=73 0.65-0.72（Option B/C marker 全保留）。**化學評估 0 hits 非 regression**（其他 5/5 通、score 與 pre-baseline 一致；query 太 narrow + threshold 0.22；chem_sss_2007_2018 仲喺 broader Option C 未處理隊列）。
- **Cleanup：** Leonard paste DROP `__rls_inspect_temp` + final verify block 落 Dashboard，result 確認 `{wiki_chunks_rls:true, policy_count:1, anon_grants:["SELECT"], inspect_fn_dropped:true}`。Temp SECURITY DEFINER function 清走、schema clean。
- **Supabase Dashboard 警報：** post-APPLY 數分鐘 - 幾小時內 scanner cycle 應 auto-clear「rls_disabled_in_public」alert（async、非阻塞 PERSIST 嘅 verify；下次 Leonard 開 Dashboard 順手 confirm）。
- **§8 codified：** 寫成 PMS §C.4 doc drift 修正（live anon 真實 grants）+ §E.10 entry partial resolution（read-only-disclosure + anon-write attack-surface = RESOLVED；admin-login client-side gate 仍 OPEN，獨立 issue）+ §E.14 延伸（Option C broader 嘅 service-role upload path 受惠：service_role bypass RLS、driver 不需改）+ §D「INSPECT live Supabase catalog via temp SECURITY DEFINER RPC」workaround codified（path 限制 + apply ritual）。
- **broader Option C 狀態：** tasks #3-#7 keep pending；`dev/vault/repage_pdfs.py` PILOT_LEGACY/PILOT_OUT 已 +10 entries（benign prep）；resume 點 = task #3 Gate 1（等 Leonard 重新明示 `--write` 走 batch-1）。
- **Sources changed（commit+push 指定檔）：** Draft: `dev/vault/repage_pdfs.py`（broader Option C +10 entries dict prep work，benign keep-in-tree）; `dev/SESSION_LOG` / `SESSION_HANDOFF` / `PROJECT_MASTER_SPEC` / `CODEBASE_CONTEXT` / `HANDOFF_PACKAGE`。Supabase live（非 git）：`wiki_chunks` RLS=ON + 1 policy + anon/authenticated GRANTS = SELECT only。

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| External service / config change（Supabase RLS + GRANT hardening on wiki_chunks 生產 live）| PROJECT_MASTER_SPEC §C.4 anon GRANTS truth-pass + §E.10 partial resolution + §E.13 延伸（INVOKER RPC + RLS interaction） + §D「INSPECT via temp SECURITY DEFINER RPC」workaround；CODEBASE_CONTEXT External Services Supabase notes + AI Maintenance Log +S121；HANDOFF_PACKAGE §2 wiki_chunks state + §3 risks | ✓ Done |
| Security risk resolution（§E.10 family、partial — RLS family closed）| SESSION_HANDOFF Known Risks update（RLS critical → resolved，admin-login client-side 仍 OPEN 獨立保留）+ Open Priorities regen | ✓ Done |
| Regression + Lessons-to-Rule（§8）| §E.10 codify partial-fix + §D codify INSPECT workaround + auto-memory project_supabase_security note | ✓ Done |
| Doc drift（PMS §C.4 anon GRANT claim vs live state）| PMS §C.4 update real anon grants（pre-S121: full set；post-S121: SELECT only）| ✓ Done |
| broader Option C pause（in-flight，非 abandoned）| SESSION_HANDOFF Open Priorities 標記 paused / resume gate + SESSION_LOG status 記低 + 保留 `dev/vault/repage_pdfs.py` dict +10 entries（benign prep）| ✓ Done |

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

⚠️ 然後讀 dev/HANDOFF_PACKAGE.md（可信狀態快照）。起手務必自行 verify git HEAD + knowledge.json._meta.stats vs SESSION_HANDOFF Current Baseline，並實測 egress（onrender /health，勿照抄）。

⚠️ Repo root = "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"（路徑含空格，shell 必須雙引號絕對路徑）。Channel B/retrieval PoC 喺姊妹資料夾 "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Testing/poc-retrieval/"（唔喺 git、Draft 零接觸）。`python` 唔存在用 `python3`。git commit+push 由 Claude 做（指定檔勿 -A）。Agent team 係預設模式。回覆用中文。

S121（CLOSED 2026-05-20，Leonard「收工」）：**Supabase critical security incident response 完成生產 live + 0 regression**。HEAD `fd22e0a` 同步 origin/main commit+push 完成；後置 closeout commit 跟住推。Trigger = Leonard 截停 broader Option C batch-1 step 4 + 出示 Dashboard 警報「rls_disabled_in_public」on `wiki_chunks`。INSPECT 揭發**遠超警報 surface**：anon GRANTS 實有 SELECT+INSERT+UPDATE+DELETE+TRUNCATE+REFERENCES+TRIGGER（PMS §C.4 doc drift；任何 anon 用戶可清空/投毒 wiki_chunks）。§3 HIGH-risk PLAN→ Leonard Dashboard 親手 paste：ENABLE RLS + CREATE POLICY `wiki_chunks_anon_read` SELECT anon,authenticated USING(true) + REVOKE 6 write privilege × 2 role。Post-APPLY re-INSPECT 確認 live state 完美對應；Channel B 5/6 live smoke PASS（採購 0.66/0.62/0.638 與 pre-baseline byte-identical / 幼稚園收生 g26 p=2/4 0.696 / 學校行政手冊 sag p=1 / 教師專業操守 sag p=205+g05 p=30+sag p=73 / 化學 sci_jss+chem_sss）；「化學評估」0 hits 非 regression（query 太 narrow、其他 5 query 健康）。Cleanup：DROP temp inspect function、schema clean。Dashboard 警報 async clear（下次開 Dashboard 順手 confirm）。

Current objective and progress state:
- **Supabase wiki_chunks RLS hardening 完成生產 live**：RLS ON + 1 anon-read SELECT policy + anon/authenticated GRANTS = SELECT only + service_role 全 grants 保留（broader Option C upload 不受影響）。
- **broader Option C batch-1 = paused 等 resume**：tasks #3-#7 pending；`dev/vault/repage_pdfs.py` PILOT_LEGACY/PILOT_OUT +10 entries（10 sources：tech_kla_guide_2017 / eng_lit_guide_2023 / ls_jss_2010 / religious_edu_jss_2024 / geog_sss_2007_2022 / ces_jss_2024 / phys_sss_2007_2015 / chi_hist_sss_2007_2015 / chem_sss_2007_2018 / geog_jss）已落 + repage dry-run 8/10 OK / 2 URL-encoding fail（geog_sss_2007_2022 / ces_jss_2024 含空格、修法明確）；Gate 1 等 Leonard 重新明示 `--write` 走。
- §E.10 partial resolution（RLS critical family CLOSED；admin-login client-side gate 仍 OPEN 獨立保留）。
- Q4（Channel A→`knowledge.json`→下游 Circular System 對外契約）deferred 獨立 track；Stage-2 closed-as-non-viable 勿復活。

Pending tasks in priority order:
1. **broader Option C batch-1 resume**（tasks #3-#7 pending；先 fix 2 URL-encoding fail：repage_pdfs.py `fetch_pdf` 加 `urllib.parse.quote` for path-with-space PDFs；之後 Gate 1 等 Leonard 明示 `--write`）。
2. **broader Option C batch-2 ~ batch-6**（51 marker-less PDFs 未掂；batch-1 完成 + verified 後 Leonard 排）。
3. 細項 backlog（低優先）：local `wiki_index.json` ↔ Supabase reconcile / sag freshness metadata 2025-11→2026-05 / g06 vs pri_curr_guide_2024 SOURCE_ALIASES dedup polish。
4. 既有 deferred：🔴 §E.10 admin-login client-side gate（RLS family 已修、admin-login 仍 OPEN）；🔴 Supabase `57014` timeout（生產可用性 free-tier transient，retry 即恢復）/ probes=8 live 已 reconfirm 經本 session INSPECT；🔴 FAIL-A Circular 注入 regression（record-only）；P2 分類148/P3；Mobile UI P2；HKEAA；FAIL-B `semanticRegression.ts:292` stale 1.3.1。
5. Q4 對外契約收斂（deferred 獨立 track）。

Key files changed this session (全部 commit+push)：
- Draft（modified）：`dev/vault/repage_pdfs.py`（PILOT_LEGACY/PILOT_OUT +10 entries，broader Option C batch-1 prep；benign keep-in-tree）；dev/SESSION_LOG / SESSION_HANDOFF / PROJECT_MASTER_SPEC / CODEBASE_CONTEXT / HANDOFF_PACKAGE。
- Supabase live（**非 git，Leonard Dashboard 親手 DDL applied**）：`public.wiki_chunks` RLS=ON + policy `wiki_chunks_anon_read` SELECT TO anon,authenticated USING(true) + anon/authenticated GRANTS REVOKE 6 privilege（剩 SELECT only）；temp inspect RPC DROPped after use；service_role grants/`match_wiki_chunks` RPC 屬性全部 unchanged。
- Testing/：（無 PoC 改動本 session）。

Known risks / blockers / cautions:
- **新 §D codified workaround**：Claude service-role REST 對 `pg_catalog` / `information_schema` HTTP 406；INSPECT live catalog 須 wrap SECURITY DEFINER RPC（Leonard paste APPLY → Claude call RPC → Leonard paste DROP），三步 ritual。生產 DDL 嘅 Dashboard-only lock 不變（§C.4 / §E.13）。
- **§E.14 §8 教訓延伸**：service_role bypass RLS（PostgreSQL default + Supabase same）→ Option C broader 嘅 `cb3_b2_pagecarry_migrate.py` driver service-role upload path **不受 RLS 影響、唔需改**；driver 一行唔改可 resume。**新前置條件**：寫任何「以 anon key 改 wiki_chunks」嘅 path = 死路（RLS deny + GRANT REVOKE 雙重攔截、設計如此），如果未來需要 anon-write 必須 §3 HIGH-risk + 新 policy。
- broader Option C 2 URL-encoding fail（geog_sss_2007_2022 / ces_jss_2024 path 含空格）需 `repage_pdfs.py` `fetch_pdf` 加 URL-encoding（細 fix、resume 前一次過 patch、預估 5 分鐘）。
- 暫無 RLS-induced regression（5/6 live smoke PASS、化學評估 0 hits 屬 query-relevance 非 RLS）。仍要監察 Render auto-deploy + 任何 anon-side 操作（e.g. 將來如果加 anon-write feature）。
- 既有 risks：🔴 §E.10 admin-login client-side gate（OPEN，獨立 family，未掂）；🔴 Supabase free-tier 57014 transient（retry 即恢復、非 regression）；🔴 FAIL-A 注入 regression（record-only）；§3c FAIL-A/B record-only；q.html/A·AB code path/backend `/channel-a`·`/combined` endpoint dormant 可逆勿清；Q4 deferred 未明示勿掂；Stage-2 closed 勿復活。
- egress 間歇每次自測；EDB PDF 永遠用 `url_primary` 勿 `url_landing`（§E.12）；路徑空格雙引號；Testing/ 喺 Draft git 外；改 Draft code/data commit 必入 SESSION_LOG（已遵）。

Validation status:
- PASS RLS hardening：INSPECT pre/post comparison（anon 7-grant → SELECT only；RLS off→on；policy 0→1 wiki_chunks_anon_read）+ Channel B 5/6 live smoke 0 regression + Cleanup verify clean。
- PENDING（async）：Supabase Dashboard「rls_disabled_in_public」alert auto-clear（下次 Leonard 開 Dashboard 順手 confirm；非阻塞）。
- OPEN（非 pending-blocker）：broader Option C batch-1 resume 等 Leonard / 2 URL-encoding fail 補；既有 deferred 同 S120。

Post-startup first action: 完成 §1 起手序 + HANDOFF_PACKAGE + 自測（git HEAD / knowledge.json._meta.stats vs baseline / egress 實測）後，**S121 已 closeout — Supabase RLS critical hardening 生產 live + 5/6 Channel B smoke 0 regression + commit/push 完成 + Dashboard 警報 async clear pending（Leonard 下次開 Dashboard 順手 confirm）—— 第一件事＝問 Leonard：(a) broader Option C batch-1 而家 resume（先 fix 2 URL-encoding fail、然後 Gate 1 走 --write）？(b) 抑或先做其他（freshness metadata polish / §E.10 admin-login / 等等）？**未 Leonard 明示前**唔好自行 resume broader Option C / 改其他 Draft / 掂 Q4 契約**。碰 admin/auth/公開推送前必讀 §E.10。CB-3 / B-only 方向 / Q4 track / §8 incident 詳見 auto-memory project_direction_review；Supabase RLS workaround details 詳見 PMS §D.18 + §C.4 + §E.10 + §E.13。
```

---
