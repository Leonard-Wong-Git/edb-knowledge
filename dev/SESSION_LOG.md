# Session Log

<!-- Archives: dev/archive/ — entries moved when >400 lines or oldest entry >30 days -->

## 2026-06-05 Session 143 — Channel B 廣度試用 + QA recall fix（qa_inspection 路由）+ Q4 Phase 1 凍結 Channel A（docs-only）；生產 live、0 regression — CLOSED

- **ID:** Claude_20260605_1012
- **Trigger:** 新 session 起手自測（verify-load-bearing-state）→ Leonard 揀「先試用 Channel B 廣度（建議）」→「先快補 QA recall gap（建議）」。
- **起手自測全對賬:** git HEAD `6612ef9`(S142 closeout)==origin/main ✓ / Channel A facts 455 ✓ / 公開 guidelines 152 v2.5.0 ✓ / source_registry 203 ✓ / Supabase wiki_chunks **10,594**（service_key REST `Content-Range 0-0/10594` 雙讀防偽零）✓ / onrender /health 200 warm cache_a=455 ✓。
- **§3 Risk:** HIGH（涉 Render deploy）；Leonard 選項授權；純 routing additive/可逆（git revert 即還原、0 data mutation）。

### Channel B 廣度試用（read-only live smoke、18 query paced 8s 防 429）
- **substantially「夠用」**：14/18 乾淨命中正確源 + **17/18 帶頁碼（北極星）** + 3/3 synth 答案質素好（危機應變/統一派位/內部監控防貪，繁中精簡附源帶頁）。6 條 S142 新擴 route 全 engage。
- 4 miss 分類（playbook `throttled-api-not-empty-data`）：斜坡/遣散費/和諧校園 = **benign ranking competition**（薄身 net-new 專檔被 SAG/g04 壓、但內容帶頁有 surface；specific query「長期服務金」→ long_service_payment_guide #5 surface 證實；handoff 已記 benign）；**「視學」→0 = 唯一真 gap**（重現確認 HTTP 200、非 throttle）。

### QA recall fix（§3d 矩陣全 PASS）
- **根因:** `視學` route 入 gov_admin，但 gov_admin **無 query expansion**（S142 防 over-expansion）+ QA docs 用新詞（校外評核/自我評估/問責）→ 短 token embedding 對唔齊 → under-recall。
- **Fix（`backend/src/api/searchChannelB.ts` 單檔 +30/−5）:** 拆 **`qa_inspection`** 專 route 置 gov_admin 前 first-match（regex: 視學/校外評核/學校自我評估/自我評估/表現指標/質素保證/問責架構/問責/校本管理；用「自我評估」非 bare「評估」唔偷 curriculum）+ tight SOURCE_SET〔sse_tools_2025/perf_indicators_2022/edbc15_2022_accountability + sag + role_facts_general〕+ 針對性 QUERY_EXPANSIONS〔校外評核/自我評估/表現指標/質素保證/問責/校本管理/學校發展〕。over-expansion-safe = tight set + per-source quota；QA terms 由 gov_admin 移出（one-place §3b）。
- **QC:** `npm run check`/`build` exit 0 → commit `58b5705` push origin/main → Render deploy → poll「視學」0→5 確認 live。
- **對抗 regression smoke 17/17 HIT、0 QA-doc 洩漏:** qa 5/5（視學/校外評核/學校自我評估/表現指標/問責架構 → 三大 QA docs 帶頁 0.61-0.75）；gov_admin 5/5（防貪→icac / 更改校名→sch_name / 校舍→major_repairs / 學校發展計劃→sdp / 增設校舍→sch_extension，零 QA 洩漏 = split 乾淨）；safety/curriculum/finance/hr/student_support/placement 7/7 零回歸。

### Q4 Phase 1 — 凍結 Channel A（docs-only freeze；Leonard ③→① phased、明示「執行 Phase 1」）
- **前提（verify-based）:** Channel A 已 de-facto 靜止（`candidate_queue.json` 空、role_facts 自 S111 未變）→ freeze = K1-side docs-only state 形式化，**0 data mutation、knowledge.json 唔郁（凍 @455）、guidelines.json 不凍（非 Channel A、續 live @152）、backend endpoint 不刪、下游零改變**。
- **CHANGE（docs-only）:** PMS §F.2（Q4 line→Phase 1 EXECUTED）+ §B.1（pipeline 照常→frozen）；CODEBASE Key Decisions（Q4 deferred→Phase 1 done）+ AI Maintenance Log；K1_API_SPEC root+dev（凍結 advisory、不洩 Channel B 內部詞）。
- **明確唔掂:** knowledge.json / role_facts.json / guidelines.json / Supabase / backend endpoint / 下游 Circular System repo（§A.3）/ policy_signals。0 server-side admin（不 reopen §E.10）。
- **Phase 2（後續、跨 repo、待 Leonard）:** 選項① 下游 Circular System 改消費 Channel B；K1 只備 migration spec、絕不掂對方 repo。選項② 不採（衝突 §F.6）。
- **Rollback:** git revert docs commit 即 un-freeze（資料從未 touch）。

### Sources changed
- `backend/src/api/searchChannelB.ts`（SOURCE_SETS + TOPIC_KEYWORDS + QUERY_EXPANSIONS 加 qa_inspection、QA terms/sources 由 gov_admin 移出）。commit `58b5705`（指定檔勿 -A）origin/main。
- **NOT modified:** Supabase / knowledge.json / guidelines.json / role_facts.json / vault / source_registry.json / app.html。
- **PERSIST docs:** SESSION_HANDOFF（Baseline #1 HEAD 凍-S125 reconcile→58b5705 + #3 append S143 + Open Priorities ✅ annotation）；本 entry。

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| Product behavior / tuning change (QA route fix) | SESSION_HANDOFF baseline/priorities/risks; SESSION_LOG task entry + QC evidence | ✓ Done |
| Long-term spec / locked decision / architecture invariant change (Q4 Phase 1 Channel A freeze) | PMS §F.2/§B.1; CODEBASE Key Decisions + AI Maintenance Log; SESSION_HANDOFF Open Priorities + ✅ annotation; K1_API_SPEC root+dev advisory | ✓ Done |

CODEBASE_CONTEXT：QA fix = N/A（純 routing）；Q4 Phase 1 = Key Decisions + AI Maintenance Log updated（locked-decision / direction shift）。0 knowledge.json/guidelines.json/role_facts/Supabase/backend-endpoint mutation。

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

⚠️ 然後讀 dev/HANDOFF_PACKAGE.md（可信狀態快照）。起手務必自行 verify git HEAD + knowledge.json._meta.stats + Supabase total vs SESSION_HANDOFF Current Baseline，並實測 egress（onrender /health，勿照抄）。S135-S143 證實 EDB + onrender + Supabase + GitHub Pages egress 均通；仍每次自測。

⚠️ Repo root = "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"（路徑含空格，shell 必須雙引號絕對路徑）。`python` 唔存在用 `python3`。git commit+push 由 Claude 做（指定檔勿 -A）。Agent team 係預設模式。回覆用中文。

S143 (2026-06-05)：**Channel B 廣度確認「夠用」+ QA recall fix（qa_inspection route）+ Q4 Phase 1 凍結 Channel A — 全 live、0 regression、0 outstanding bug**。HEAD origin/main `9978ecc` 起手自行 verify。
- Channel B 廣度試用 18 query：substantially「夠用」（14/18 命中 + 17/18 帶頁 + synth 質素好）；3 miss = benign ranking competition。
- QA fix：`searchChannelB.ts` 拆 `qa_inspection` 專route（視學/校外評核/自我評估/表現指標/問責/校本管理 由 gov_admin 移出 + 針對性 expansion；tight SOURCE_SET + per-source quota = over-expansion-safe）→ 視學 0→5、regression 17/17、0 QA-doc 洩漏。commit 58b5705。
- **Q4 Phase 1 凍結 Channel A（Leonard 明示執行、③→① phased）= docs-only freeze**：knowledge.json 凍 @455 停更、schema 不變、下游零改變、pipeline dormant 可逆、guidelines.json 不凍續 live。PMS §F.2/§B.1 + CODEBASE + K1_API_SPEC root+dev。commit 9978ecc。

Current objective and progress state:
- **下一步 = Q4 Phase 2（下游 Circular System 轉 Channel B）= 跨 repo、Leonard 喺下游 repo 主導**。K1 只備 migration spec、**絕不 mount／改對方 repo（§A.3）**；需 Leonard 先定 target 整合模型（query-time 搜尋 API per circular？定 Channel-B export？）先可出 K1-side spec。**未 Leonard 明示勿自行起 Phase 2。**
- Baseline：Supabase 10,594 / registry 203 / 公開 guidelines.json 152 v2.5.0 / 公開 knowledge.json 455 v2.3.0（Q4 Phase 1 FROZEN）/ brand live policychecker.wongfu.net。**0 outstanding bug**。

Pending tasks in priority order:
1. **Q4 Phase 2（待 Leonard 跨 repo + 設計輸入）**：下游改消費 Channel B；Leonard 定 target 模型 → K1 出 migration spec（K1-side 可逆部分 vs 下游 repo 需 Leonard）。**勿自行掂下游 Circular System repo。**
2. **觀察（非阻塞）**：freshness scheduled 週跑開 Issue；57014 cold-start mask；薄身新源（slope_rmi/long_service/edbc18_2008_harmonious 2chunks 等）generic query 被 sag/g04 壓 = benign ranking competition、specific query surface 到；knowledge.json.stats build-time 舊值（未越界改）。
3. 既有 deferred：§8b rule 2 automation / §6 通函 ASPX 驅動（ROI 低）/ Suppl_guide held / §E.10(a) ACCEPTED / FAIL-A / stat_fact 2025/26 / SESSION_HANDOFF Baseline #1 巨型 stale wall 收斂 / dev/K1_API_SPEC.md untracked stale mirror。

Key files changed this session (S143):
- backend/src/api/searchChannelB.ts（qa_inspection route）；dev/PROJECT_MASTER_SPEC.md（§F.2/§B.1 Q4 Phase 1）；K1_API_SPEC.md（凍結 advisory）；dev/CODEBASE_CONTEXT.md（Key Decisions + AI log）；dev/SESSION_HANDOFF/LOG。0 knowledge.json/guidelines.json/role_facts/Supabase mutation。commits 58b5705 / 1add3a0 / 9978ecc。

Known risks / blockers / cautions:
- 🟢 0 outstanding bug。S143 全可逆（QA fix 純 routing additive；Q4 Phase 1 docs-only 0 data touch）。
- 🔴 **Q4 Phase 2 不可逆對外效果 + 跨 repo、待 Leonard**：勿自行掂下游 Circular System repo（§A.3）/ 勿手寫 knowledge.json / 勿手寫 guidelines.json（build_guidelines.py）/ 勿自行 un-freeze Channel A。
- 既有不變: Channel A frozen @455（Q4 Phase 1）；57014 transient(S139 retry); FAIL-A(record-only); §E.10(a) ACCEPTED conditional; q.html/A·AB dormant 勿清; Stage-2 closed; egress 每次自測; 路徑空格雙引號; wiki_chunks 欄名 `text`; g14/gifted/sen_curr_area 結構天花板勿再 ingest; 改 Draft code/data commit 必入 SESSION_LOG; init_backup gitignored。

Validation status:
- QA fix：typecheck/build exit 0 + 對抗 regression smoke 17/17 + 0 QA-doc 洩漏 + 視學 0→5 帶頁。Q4 Phase 1：git diff docs-only 0 data touch + 本地 455/152 + live 公開端點 455/152（下游零改變）。Supabase 10,594 雙讀 verified。§4a SESSION_LOG 210 行 < 400、未觸發 archive。

Post-startup first action: 完成 §1 起手序 + HANDOFF_PACKAGE + 自測（git HEAD 9978ecc / facts 455 / Supabase 10,594 / guidelines 152 / 公開 knowledge.json 455 FROZEN / onrender /health）+ playbook INDEX 後，問 Leonard Q4 Phase 2 點推（要佢先定下游 target 整合模型）。**未 Leonard 明示前，勿自行掂下游 Circular System repo / 勿 un-freeze Channel A / 勿手寫 knowledge.json·guidelines.json / 勿 reopen §E.10 / 勿動 Stage-2 / 勿再 ingest 結構天花板源。**
```

## 2026-06-04 Session 142 — EDB 全覆蓋 gap sweep（逐範疇；Channel B 補到「夠用」為 Q4 鋪路）— RUNNING

- **ID:** Claude_20260604_2100
- **Trigger:** Leonard `/goal「就照你建議、做齊功課 1+2、抓取分析審核入庫」` + `/workflow`。**功課 1 = Q4 對外契約收斂（關 Channel A + 下游轉 Channel B）= sequenced 在 Channel B「夠用」之後、且係不可逆對外契約 → 留最後一步交 Leonard 撳掣，grind 途中不自行斬下游（§5）**。**功課 2 = EDB 全站政策文件 gap sweep = 主線 grind**。
- **Scope（Leonard-locked 三項）:** (1) 相關性=政策/指引/通函全文 PDF（剔 forms/exemplars/海報/語言版本 dup/統計表）；(2) ingest 審批=「就照你建議」自主推進（agent-team adversarial audit 作閘）；(3) 逐範疇分批。
- **架構約束:** sub-agent egress 被 deny（S138）+ Supabase 串行 → 不用 Workflow tool 並發；用「主爬 + agent-team 純 local 審核」模式（S140 驗證）。
- **EDB 範疇 roadmap（9 pass）:** 1.學校行政及管理 2.教師/人事 3.學生訓育輔導支援 4.校園安全 5.收生/學位分配 6.通函EDBC/EDBCM 7.SEN（核心已做、查漏）8.課程（飽和、查漏）9.雜（非華語/健康校園/IT/國安）。

### §1 學校行政及管理 ✅（35 文件入庫、+298 chunks、4 路由、生產 live、0 regression）
- **抓取:** 爬 sch-admin section 9 子範疇 = 137 PDF。
- **審核（agent-team）:** 3 curate agent（slice A/B/C 純 local 判 KEEP/DUP/NOISE）→ 砍 94 forms/通知書/worked-example/rate-sheet/海報/單張/合約樣本/contact-list/flowchart → 44 KEEP；1 adversarial audit agent（Explore）→ dedup（AD02003C i73=i121）+ value-tier（21 TIER-1 + 22 TIER-2）。Leonard 逐項過 → 照建議（剔 79/80/90/121/122/125/126 + 英文版）。
- **egress 核實:** 36 fetch、35 mojibake-CLEAN、剔 #111（英文版 cjk=0）→ **35 ingest**。真標題核到（#37 ICAC 防貪 98p / #102 通函 / #83-84 2026-04 更新）。
- **入庫:** registry 152→**187**（+35 source_type=pdf、content_hash seed）；35 vault repaged（markers==pages）；cb3_b2 **del=0 ins=298 純加法**；Supabase 9,963→**10,261**；driver 17th-validation 0 incident。
- **路由（backend searchChannelB.ts）:** finance +2、hr_admin +10；**NEW gov_admin route（14：表現指標/自評/問責/防貪/籌款/校舍修葺/增設校舍/改校名/SDP/保險）+ safety route（9：消防/職安/實驗室/氣體/熱帶氣旋/安全管理委員會/斜坡維修）**（TOPIC_KEYWORDS first-match 置 sen 後 curriculum 前 + SOURCE_SETS + QUERY_EXPANSIONS）。typecheck+build exit 0。
- **§3 CHANGE divergence（smoke 揪出 + 修）:** 初版把所有新文件詞塞入 QUERY_EXPANSIONS → over-expansion 稀釋 focused query（熱帶氣旋壓住消防、edbc14 保障學童壓住 g04 批假）→ **修：hr_admin expansion 還原、safety/gov_admin 不加 expansion（靠 SOURCE_SET filter + query 本身詞）**。呼應 playbook `llm-deterministic-postpass`。
- **commit:** `80368f8`（ingest+路由）→ `934775d`（expansion fix）origin/main → Render deploy。
- **QC live smoke（redeploy 後 paced，防 429）全 PASS:** 批假→g04 #1 @0.719 / 消防→fire #1 @0.703 / 表現指標→perf #1+sse_tools / 基本法測試→blnst surface / 更改校名→sch_name #1/#2 / 防貪→icac #1 / 熱帶氣旋→tropical #1-3 / 過剩教師→surplus / bank_choice #1 / **regression：英文科→curriculum 零污染、sen→g19/g06 非回歸、批假→g04（修後）**。全帶頁碼。
- **lesson:** (1) hub section 爬出 137 → 真政策得 35（74% 噪音，S140 教訓 §section 級再印證）；(2) over-expansion 稀釋 = 新 route 加 SOURCE_SET 已夠、唔好再塞 expansion；(3) live smoke 連發必撞 429 → paced 重測分清 throttle vs 真回歸（throttled-api-not-empty-data）。

### §2 教師/人事 ✅（3 文件入庫、+87 chunks、cpd/hr_admin 路由）
- **抓取/dedup:** 爬 /tc/teacher/ 12 PDF；qualification-training-development CPD 頁 = 0 直連 PDF（HTML-only 結構天花板，如 g14）。注意 §1 已掃 sch-admin/about-sch-staff（appointment/BLNST/公積金/薪金）→ §2 避重複。
- **審核 + egress:** 12 → 真政策 3（剔 checklist/日薪率rate-sheet/MPF對沖 PPT×3/FAQ + **guidelines_tc=DUP of g05**〔g05 已 29 page-carried chunks〕）。egress 全 CLEAN。
- **入庫:** registry 187→**190**；cb3_b2 del=0 ins=87；Supabase 10,261→**10,348**。tdtf_report_2019 教師專業發展專責小組報告(62p)→cpd；supply_teacher_guide 代課教師指引(10p)+long_service_payment_guide 遣散費長服金指引(6p)→hr_admin（keyword +遣散費/長期服務金/長服金）。typecheck+build exit 0。commit `2cf77d7`。
- **lesson:** §2 大量內容同 §1 sch-admin/about-sch-staff 重疊（HR 散落兩個 EDB top-section）→ sweep 必 cross-section dedup；CPD framework 頁 HTML-only = 結構天花板。

### §3 學生訓育輔導支援 ✅（7 文件入庫、+186 chunks、NEW student_support 路由）
- **抓取/curate:** 爬 student-guidance + 自殺預防 + 危機處理 = 80 PDF → noise-strip 39 → egress-verify 14 → 真全文政策 **7**。**剔走：MRR 強制舉報簡介會/概覽/校長分享×4（slides，cjk 極疏；MRR 政策由 EDBC15/2025 circular 覆蓋）+ 大埔火災 TP_* 事件支援資源（非政策）+ 培訓課程/繪本/board-game/lesson-plan**。
- **入庫:** registry 190→**197**；cb3_b2 del=0 ins=186；Supabase 10,348→**10,534**。7 源：EDBC015/2021 生涯規劃+推行框架(16p)、EDBC18/2008 締造和諧校園、EDBC15/2025 處理懷疑虐待兒童及家暴(12p)、EDBCM83/2020 關顧學生、**crisis_mgmt_handbook 學校危機處理手冊(82p)**、kg_crisis_mgmt 幼稚園危機處理(39p)。
- **路由:** NEW `student_support`（TOPIC_KEYWORDS 置 conduct 後 + SOURCE_SET 含既有 g16/g17 + sag + role_facts_student；無 expansion 防稀釋）。commit `2070c44`。typecheck+build exit 0。
- **lesson:** student-welfare section 噪音率最高（80→7=91% 噪音：大量學校分享/簡報/單張/事件資源）；MRR slides ≠ 全文指引（egress cjk-density 分辨）。

### §4 校園安全 + 健康校園 ✅（core 已§1；+3 健康校園、+14 chunks）
- **校園安全 core 已喺 §1 safety route**（消防/職安/實驗室/氣體/熱帶氣旋/斜坡/安全管理委員會，由 sch-admin/about-sch/sch-safety 31 PDF curate）→ §4 唔重做。
- **健康校園 net-new 3**：EDBC100/2002（禁毒健康校園 circular）、hsp_framework（健康校園政策架構）、hsp_drug_testing_2026（含測檢元素計劃）。剔 brief/化驗所操作（low-cjk slides）。registry 197→**200**；Supabase 10,534→**10,548**；route=student_support（+健康校園/禁毒/藥物測試 keyword）。commit `3d815c0`。

### §5 收生/學位分配 ✅（3 文件、+46 chunks、NEW placement 路由）
- 爬 spa-systems 7 子頁 51 PDF → 真政策 3（多家長表格/FAQ/名單/HTML 機制 = NOISE）。EDBC18/2019 中學學位分配辦法(11p) + STIMS 學生資料管理系統指引(21p) + 中四學位安排機制(2026)。剔 P1 addendum（英文空）。registry 200→**203**；Supabase 10,548→**10,594**；NEW placement route（P1/SSPA/S4/STIMS）。commit 見 push。

### §6-9 評估（bounded / 飽和，0 ingest）+ SWEEP 核心完成
- **§6 通函 EDBC/EDBCM:** EDB circular 系統 = ASP.NET app（`td.circularResultRow` + ViewState，PMS §E 記）→ 不可靜態枚舉。高價值 admin 通函已喺 §1-5 經 section 連結捕捉（共 ~18 條 EDBC/EDBCM 入庫）。Exhaustive 枚舉需驅動 ASPX 表單（成本高 + 多數 operational/dated/topic-specific noise）→ out-of-scope，文檔化。
- **§7 SEN:** S141 已補（sea_guide + g10/g19 + g06）；g14/gifted = 結構天花板（S141 documented）。0 net-new。
- **§8 課程:** ~130 curriculum docs 已飽和（KLA/各科 C&A/通函齊全）。0 net-new。
- **§9 雜:** 非華語 g09 ✅、國安 eng_nat_sec_2025+nat_sec_edu ✅、IT g28 ✅。Suppl_guide held（S140 待人核）。0 net-new。
- **SWEEP 核心完成：§1-5（學校行政/教師人事/學生支援/安全健康/收生派位）= EDB「營運學校」高價值核心全掃，+51 政策文件 / +631 chunks / 6 新路由（gov_admin/safety/student_support/placement + 擴 finance/hr_admin/cpd）。Channel B 對學校管理人員 substantially「夠用」= Q4 前置條件達成。**

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

⚠️ 然後讀 dev/HANDOFF_PACKAGE.md（可信狀態快照）。起手務必自行 verify git HEAD + knowledge.json._meta.stats + Supabase total vs SESSION_HANDOFF Current Baseline，並實測 egress（onrender /health，勿照抄）。S135-S142 證實 EDB + onrender + Supabase egress 均通；仍每次自測。

⚠️ Repo root = "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"（路徑含空格，shell 必須雙引號絕對路徑）。`python` 唔存在用 `python3`。git commit+push 由 Claude 做（指定檔勿 -A）。Agent team 係預設模式。回覆用中文。

S142 (2026-06-04/05)：**EDB 全覆蓋 gap sweep §1-5 完成、push live、QC 全 PASS**。HEAD origin/main 起手自行 verify。
- Leonard /goal「做齊1+2、抓取分析審核入庫」+ /workflow。逐範疇掃 EDB 站政策/指引/通函全文 PDF：主爬→agent-team(curate+adversarial audit)→egress 逐份核實→嚴格相關性篩→del=0 batch ingest→路由→deploy→paced smoke。
- **§1 學校行政(+35) §2 教師人事(+3) §3 學生訓育支援(+7) §4 健康校園(+3,安全 core 已§1) §5 收生派位(+3)** = **+51 政策文件 / +631 chunks**。registry 152→**203**；Supabase 9,963→**10,594**（全 del=0 純加法可逆）。
- **6 新/擴路由**：NEW gov_admin（問責/視學/防貪/校舍/改校名/SDP）+ safety（消防/職安/熱帶氣旋/斜坡）+ student_support（生涯規劃/和諧校園/虐兒/危機處理/健康校園）+ placement（中學派位/STIMS）+ 擴 finance/hr_admin/cpd。
- **§6 通函 EDBC = ASPX app 不可靜態枚舉**（高價值已§1-5捕捉~18條）；**§7 SEN / §8 課程(~130) / §9 雜 = 已飽和/已覆蓋**。SWEEP 核心完成。
- driver cb3_b2 17→22 輪 0 incident。over-expansion regression（QUERY_EXPANSIONS 過度塞詞稀釋 focused query）自捉自修；新 route 靠 SOURCE_SET filter 唔加 expansion。

Current objective and progress state:
- **下一步 = 功課1 Q4（待 Leonard 撳掣）**：關 Channel A + 下游轉 Channel B。**不可逆對外契約 + 跨 repo（下游 Circular System 獨立 repo、PMS §A.3 勿掂）+ Leonard 定咗係最後一步** → 未明示「執行 Q4」勿自行斬下游。Channel B 已 substantially「夠用」（前置條件達成）。
- Baseline：Supabase **10,594** / registry **203** / 公開 guidelines.json 152 v2.5.0 / brand live policychecker.wongfu.net。**0 outstanding bug**。

Pending tasks in priority order:
1. **Q4 對外契約收斂（待 Leonard 明示「執行」）**：建議先實際試用新 Channel B（行政/財務/教師/學生支援/安全/派位查詢）confirm 真夠用 → 再出 §3 HIGH-risk Q4 遷移 PLAN（K1 側可逆部分 vs 下游 repo 需 Leonard 協調）。
2. **觀察（非阻塞）**：freshness scheduled 週跑開 Issue；57014 cold-start mask；新源小文件（如 edbc18_2008_harmonious 2chunks / long_service）generic query 被 sag/g04 壓 = benign ranking competition、specific query surface 到；knowledge.json.stats 仍舊（build-time、未越界改）。
3. 既有 deferred：§8b rule 2 automation / §6 通函 ASPX 驅動（ROI 低）/ Suppl_guide held / §E.10 ACCEPTED / FAIL-A。

Key files changed this session (S142):
- dev/source/source_registry.json（152→203，+51 source_type=pdf + freshness content_hash）；dev/vault/<51 新源>/（repaged，markers==pages）；backend/src/api/searchChannelB.ts（6 路由：gov_admin/safety/student_support/placement NEW + finance/hr_admin/cpd 擴 + TOPIC_KEYWORDS + QUERY_EXPANSIONS trim）；dev/SESSION_HANDOFF/LOG/CODEBASE。0 knowledge.json/guidelines.json/role_facts mutation。commits 80368f8…(closeout)。

Known risks / blockers / cautions:
- 🟢 0 outstanding bug。S142 全 del=0 純加法（git revert + Supabase DROP 可逆）。
- 🔴 **Q4 未做、不可逆、跨 repo、待 Leonard 明示**（勿自行關 Channel A / 掂下游 Circular System repo）。
- 既有不變: 57014 transient(S139 retry); FAIL-A(record-only); §E.10(a) ACCEPTED conditional; q.html/A·AB dormant 勿清; Stage-2 closed; egress 每次自測; 路徑空格雙引號; wiki_chunks 欄名 `text`; guidelines.json 勿手寫(build_guidelines.py); g14/gifted/sen_curr_area 結構天花板勿再 ingest; 改 Draft code/data commit 必入 SESSION_LOG; init_backup gitignored。

Validation status:
- 每範疇 repage Gate1 markers==pages + cb3_b2 Gate2 del=0 per-source verify + typecheck/build exit 0 + paced live smoke（防 429）全 PASS。Supabase cumulative 10,594 verified。SESSION_LOG §4a 已 archive（423→137 行，3 entries→dev/archive/SESSION_LOG_2026_Q2.md）。

Post-startup first action: 完成 §1 + HANDOFF_PACKAGE 起手序 + 自測（git HEAD / facts 455 / Supabase 10,594 / onrender /health / guidelines live 152）+ playbook INDEX 後，問 Leonard 係咪執行 Q4（或先實際試用新 Channel B 廣度）。**未 Leonard 明示「執行 Q4」前，勿關 Channel A / 勿掂下游 Circular System repo / 勿手寫 guidelines.json / 勿 reopen §E.10 / 勿動 Stage-2 / 勿再 ingest 結構天花板源。**
```

## 2026-06-04 Session 141 — SEN/資優 0-chunk 補完：sea_guide_c.pdf page-carry +51（生產 live；3 個 named id 證實結構天花板；0 knowledge/guidelines mutation）

- **ID:** Claude_20260604_1500
- **Trigger:** Leonard 開工選下一階段方向 = **「g14+資優 SEN 補完」**（handoff Open Priorities #1(a)：g14/sen_curr_area/gifted_policy_docs 仍 0 Supabase chunks、SEN-adjacent gap）。
- **§3 Risk:** HIGH（外部 EDB fetch + Supabase data mutation + 線上 deploy）→ 出 PLAN 等確認 → Phase-0 read-only crawl → STOP gate 報 curate → Leonard 拍板 → Phase 1-2 mutation。

### 起手自測（verify-load-bearing-state-not-docs）
- HEAD `e8bddaa`(S140 closeout)==origin/main ✓ / Channel A facts 455 ✓ / role_facts.json byte-identical(md5) ✓ / 公開 guidelines live 152 v2.5.0 ✓ / onrender /health 200(冷啟喚醒 11.4s) ✓ / Supabase total 9,912 ✓。
- 雙讀(防 429 偽零)確認 g14=0 / sen_curr_area=0 / gifted_policy_docs=0（claim 屬實）；g10=129 g19=116 sanity ✓。

### Phase-0 read-only crawl（3 個 named id；0 mutation）
- **g14《校本資優培育課程指引》= 純 HTML 14 分章**（引言+6章+附錄+參考+委員+鳴謝），EDB **無 PDF 版** → 無 `#page=N`、違北極星可追溯頁數 = **結構天花板**。gifted hub 15 PDF 係 resource kit/booklet/海報、非 g14 指引本身。
- **gifted_policy_docs = 靜態 nav-only 頁**（static HTML 只得 mega-nav、無內容文件連結）。
- **sen_curr_area = curriculum-area hub**：主 child《特殊學校課程指引》= g10（已 ingest 129）；子頁爆成 ~179 智障學生學科改編 exemplar（115+19+2+43，逐科教學示例=另一大 scope 噪音、非政策指引）。
- **唯一真‧淨增益 PDF = sea_guide_c.pdf**：《為有特殊教育需要學生提供校內考試特別安排》二零二五年九月(修訂)、46p、SENSE portal、mojibake pre-flight CLEAN（CJK 1350 / U+FFFD 0）、與 g19 ie_guide_ch.pdf 唔同檔。
- **STOP 報 Leonard** → curate「3 個 named id 真增益僅 1 份」→ Leonard 揀「只 ingest sea_guide（建議）」。

### CHANGE（Phase 1-2）
- **registry**：+`sen_exam_arrangements_2025`（source_type=pdf、url_primary=SENSE 直連 PDF、topic_tags=[student]、version_label=2025-09、freshness_metadata seeded〔content_hash e473133d…〕、notes 記 hub-discovery + 3 id 結構天花板）；151→**152**、`_meta.updated`→2026-06-04；diff 純加法（29 ins / 2 del = updated 日期 + 末尾逗號）。
- **vault**：seed header stub → `repage_pdfs.py` PILOT_LEGACY/PILOT_OUT +1 → Gate1 `--write` **46 pages = 46 markers**（stub backup→init_backup、removed）。
- **Supabase**：`cb3_b2_pagecarry_migrate.py --only sen_exam_arrangements_2025 --execute --skip-local` → **del=0 ins=51 純 INSERT**、now=51 OK；total 9,912→**9,963**；chunks 帶 `=== Page N ===`、title/url 正確。
- **backend**：`searchChannelB.ts` SOURCE_SETS.sen +`sen_exam_arrangements_2025`（S135 backfill-allowlist coupling）+ QUERY_EXPANSIONS.sen 加「校內考試特別安排/考試調適/評估調適/特別考試安排」。

### QC / Test Scenarios（§3d）
| Scenario | Expected | Actual | Result |
|---|---|---|---|
| repage Gate1 | markers==pages | 46==46 | PASS |
| cb3_b2 Gate2（新源純加法）| del=0 純 INSERT | del=0 ins=51 now=51 | PASS |
| Supabase total | 9,912→9,963 | 9,963 | PASS |
| 頁碼可追溯（北極星）| chunks 帶 `=== Page N ===` | p=1..46 confirmed | PASS |
| typecheck + build | exit 0 | check 0 / build 0 | PASS |
| Normal: 特殊教育需要 校內考試特別安排 | 新源 surface 帶頁碼 | 新源 #1 p=9 @0.74 + #6 p=44 | PASS |
| Regression bare「sen」| sen route 非回歸 | g19/g06 共存、新源 #4 | PASS |
| Regression 英文科課程指引 | NOT route sen | route curriculum cluster、零污染 | PASS |
| Broader 融合教育 SENCO | SEN corpus surface | g19 主導 + 新源 #4 帶頁碼 | PASS |

### Sources changed
- `dev/source/source_registry.json`（+1 source、151→152）；`dev/vault/sen_exam_arrangements_2025/extract_sen_exam_arrangements_2025_repaged.txt`（NEW）；`dev/vault/repage_pdfs.py`（PILOT_LEGACY/PILOT_OUT +1）；`backend/src/api/searchChannelB.ts`（SOURCE_SETS.sen + QUERY_EXPANSIONS.sen）；`dev/PROJECT_MASTER_SPEC.md`（§16 +S141 + 結構天花板釐清）；`dev/DOC_SYNC_CHECKLIST.md`（+row）；`dev/CODEBASE_CONTEXT.md`；`dev/SESSION_HANDOFF.md`；`dev/SESSION_LOG.md`。
- **NOT modified:** Supabase 其他源 / knowledge.json / guidelines.json / role_facts.json / app.html。
- commit `e7215e2`（code+data：registry/repage/vault/backend；指定檔勿 -A）origin/main；PERSIST docs 本 entry。

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| Channel-B vault source backfill / page-carry into Supabase（S122-S141 recurring）| registry + backend SOURCE_SETS/QUERY_EXPANSIONS parity + SESSION_HANDOFF baseline + SESSION_LOG + CODEBASE Directory Map/Maint Log | ✓ Row added（此前無精確 row = registry gap）+ ✓ Done |
| Long-term spec / structural-ceiling | PMS §16（g14/gifted_policy_docs/sen_curr_area 標勿再 ingest）| ✓ Done |

### lesson（§8 monitoring）
- **hub-page 真增益細**（S140 landing-curate 教訓再印證、cross-id recurrence）：handoff 假設「可沿 g10/g19 §E.12 pattern 補」，但 3 個 named id 實測係 hub/HTML-only/dup，唯一可 page-carry 得 1 份 → **verify-don't-trust + Phase-0 crawl + STOP gate 救返**（避免對結構天花板源跑無謂 ingest）。
- g14 類「HTML-only 多分章無 PDF」guideline = 結構天花板新子類（之前 9 源 = HTML-landing + xlsx）；無頁碼不入 page-carry pipeline。已 codify PMS §16。

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

⚠️ 然後讀 dev/HANDOFF_PACKAGE.md（可信狀態快照）。起手務必自行 verify git HEAD + knowledge.json._meta.stats vs SESSION_HANDOFF Current Baseline，並實測 egress（onrender /health，勿照抄）。S135-S141 證實 EDB + onrender + Supabase egress 均通；仍每次自測。

⚠️ Repo root = "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"（路徑含空格，shell 必須雙引號絕對路徑）。`python` 唔存在用 `python3`。git commit+push 由 Claude 做（指定檔勿 -A）。Agent team 係預設模式。回覆用中文。

S141 (2026-06-04)：**SEN/資優 0-chunk 補完完成、push live、QC 全 PASS**。HEAD origin/main 起手自行 verify（S141 commit `e7215e2`）。
- Leonard 揀「g14+資優 SEN 補完」→ Phase-0 read-only crawl 3 個 named 0-chunk id（g14/sen_curr_area/gifted_policy_docs）證實**全屬 hub/HTML-only/dup**（g14 純 HTML 無 PDF=結構天花板；gifted_policy_docs nav-only；sen_curr_area hub 主 child=g10）→ STOP curate「真增益僅 1 份」→ Leonard 揀只 ingest sea_guide。
- **唯一真政策 PDF** sea_guide_c.pdf《為有特殊教育需要學生提供校內考試特別安排》(2025-09、46p) → 新 registry `sen_exam_arrangements_2025`(151→152) + repage Gate1 46/46 + cb3_b2 Gate2 **del=0 ins=51**（Supabase 9,912→**9,963**）+ backend SOURCE_SETS.sen + QUERY_EXPANSIONS.sen + live SEN smoke PASS（新源 #1 p=9 帶頁碼、curriculum 零污染）。
- **3 個 named id 標結構天花板/勿再 ingest** 已 codify PMS §16。

Current objective and progress state:
- Baseline：Supabase **9,963** chunks（S141 +51 sea_guide）/ **104 marker-bearing** / CB-3 final ceiling ~88% / 公開 guidelines.json 152 v2.5.0 / registry 152 / brand live policychecker.wongfu.net。**0 outstanding bug**。

Pending tasks in priority order:
1. **下一階段方向（待 Leonard 明示）**：Q4 對外契約收斂（Channel A→knowledge.json→Circular System、3 選項、敏感、未明示勿掂）/ §8b rule 2 automation（semantic-supersede KLA-title embedding similarity check sub-agent）。
2. **觀察（非阻塞）**：freshness scheduled 週跑（週一 09:00 UTC）開 freshness-change Issue；57014 cold-start mask；knowledge.json._meta.stats.guidelines=39 stale follow-up；Suppl_guide 非華語補充指引 PDF held 待人核。
3. 既有 deferred：§E.10(a) ACCEPTED conditional / FAIL-A record-only / stat_fact 2025/26 ROI≈0 / HKEAA。

Key files changed this session:
- registry(+sen_exam_arrangements_2025 151→152)；dev/vault/sen_exam_arrangements_2025/(NEW repaged)；repage_pdfs.py(PILOT +1)；backend/searchChannelB.ts(SOURCE_SETS.sen + QUERY_EXPANSIONS.sen)；PMS §16；DOC_SYNC(+row)；CODEBASE/HANDOFF/LOG。commit `e7215e2`。

Known risks / blockers / cautions:
- 🟢 0 outstanding bug。S141 純加法（現有 chunks 0 lost、可 git revert + Supabase DROP）。
- 既有不變: 🔴 57014 transient(S139 backend retry；exhaust 後仍 400); FAIL-A(record-only); §E.10(a) ACCEPTED conditional; q.html/A·AB dormant 勿清; Q4 deferred 未明示勿掂; Stage-2 closed 勿復活; egress 每次自測; 路徑空格雙引號; wiki_chunks 欄名 `text` 非 `content`; guidelines.json 勿手寫(build_guidelines.py); 改 Draft code/data commit 必入 SESSION_LOG; init_backup gitignored; **g14/gifted_policy_docs/sen_curr_area 結構天花板勿再 ingest（PMS §16）**。

Validation status:
- repage Gate1 46/46 / cb3_b2 Gate2 del=0 ins=51 now=51 OK / Supabase 9,963 / typecheck+build exit 0 / live SEN smoke 4/4 PASS（新源帶頁碼 + curriculum 零污染 + bare sen 非回歸）。

Post-startup first action: 完成 §1 + HANDOFF_PACKAGE 起手序 + 自測（git HEAD e8bddaa→S141 commit / facts 455 / onrender /health / Supabase 9,963 / guidelines live 152）+ lazy-query playbook INDEX 後，問 Leonard 下一階段方向（Q4 對外契約〔敏感未明示勿掂〕/ §8b rule 2 automation）。可順手睇 GitHub 有冇 freshness-change Issue。未 Leonard 明示前唔好自行掂 Q4 / reopen §E.10 / 動 Stage-2 / 手寫 guidelines.json / 再 ingest g14·gifted_policy_docs·sen_curr_area（結構天花板）。
```
