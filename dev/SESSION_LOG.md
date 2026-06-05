# Session Log

<!-- Archives: dev/archive/ — entries moved when >400 lines or oldest entry >30 days -->

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

### Next Session Handoff Prompt (Verbatim)
（見下方 S142 running；逐範疇完成後更新。本 entry 為 RUNNING，§2-9 完成陸續補。）

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

## 2026-06-03 Session 140 — 公開 guidelines.json 39→148（全集投影 + landing-curate +9 + 修 3 data bug）+ NEW generator（對外契約變更；0 Supabase/backend/knowledge mutation）

- **ID:** Claude_20260603_1600
- **Trigger:** Leonard 開工選下一階段方向 = **「39→148 guidelines 擴展」**（S112 deferred-intent，前身 S111 OPEN DECISION）。
- **§3 Risk:** HIGH（對外契約變更 + 影響下游 Circular System）→ 出 PLAN + 兩輪 scope 確認後入 CHANGE。

### READ 實證（verify-don't-trust）
- registry=148（`id/title/titleShort/format/category/sub_category/level/year/isSpine/url`）；公開 schema 丟 `category/sub_category/isSpine`，top-level=topic ID。
- **冇 generator**：`bump_version.py` 只改 `_meta.version`、唔生成內容 → guidelines.json 同 registry 手動脫鈎 = drift 根源。
- category→topic 乾淨 7→7（財務採購→finance / 人力資源→hr / 課程→curriculum / 活動→activity / 學生事務→student / 資訊科技→it / 行政→general）。
- 資料質素發現：`religious_edu_jss` URL=Google grounding-redirect 壞連結 + 係 `religious_edu_jss_2024` 重複；5 組同 URL routing dup；sag/g24 同標題「學校行政手冊」分兩桶。

### §3 CHANGE divergence（scoping 階段捉到，STOP+report）
- 我原本把 3 個 `format=INDEX`（g10/g16/g28）當「導航頁」叫 Leonard 剔 → **錯**：佢哋係真指引、且原已喺公開 39。剔 = regression。修正 → 保留。重新確認 scope。

### CHANGE
- **NEW `dev/build_guidelines.py`**（registry=SSOT）：投影 schema + category→topic 映射 + 純規則 drop 9 非文件（`sub_category=='stat'` 7 + `format=='DOCX'` 1 + url 含 `vertexaisearch` 1）+ INDEX→HTML 正規化；default dry-run、`--write` mutate、`--self-test`（含回歸守衛：現有公開 id 不可消失）、`--version` 保留版本不撞 bump_version.py、原子寫入。
- `guidelines.json` 由 generator `--write --version 2.3.0 --updated 2026-06-03` 生成：**39→139**（finance 4 / hr 2 / curriculum 123 / activity 2 / student 4 / it 1 / general 3）。

### QC / Test Scenarios（§3d）
| Scenario | Expected | Actual | Result |
|---|---|---|---|
| 全集投影 | 148→139+9 drop | self-test 確認 | PASS |
| 回歸守衛 | 現有 39 條 0 lost | vs existing -0 lost | PASS |
| 非文件剔除 | 0 leak | 0 XLSX/DOCX/INDEX/vertexai | PASS |
| g10/g16/g28 保留 | present | 全present | PASS |
| Circular 篩選 | `guidelines[topic]` work | finance+curriculum=127 | PASS |
| 升版 | 2.3.0/count 139 | meta 確認 | PASS |
| idempotent | re-run 無 diff | 139→139 +0 -0 | PASS |

### Sources changed
- NEW `dev/build_guidelines.py`；`guidelines.json`（39→139）；`K1_API_SPEC.md`（root §6）/`dev/K1_API_SPEC.md`（§4）/`README.md`/`dev/PROJECT_MASTER_SPEC.md`（§B.1+§F.9）/`dev/CODEBASE_CONTEXT.md`（guidelines 行+Directory+Maint Log）/`dev/DOC_SYNC_CHECKLIST.md`（新 row）。
- **NOT modified:** app.html / Supabase / backend / knowledge.json / role_facts.json。

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| guidelines.json 公開契約 / registry 投影變更 | guidelines.json regen + K1_API_SPEC(root+dev) + README + PMS §B.1·§F.9 + CODEBASE + DOC_SYNC row | ✓ Done |
| New project doc（generator）| CODEBASE Directory Map + DOC_SYNC row | ✓ Row added |

### Follow-up（非阻塞）
- `knowledge.json._meta.stats.guidelines` 仍 = 39（另一資料檔 build-time stat、Circular 契約不消費）；升 139 屬獨立 data-touch，未越界改，留 follow-up。
- 同 URL routing dup（5 組）保留（distinct title，Circular 可自行 dedup）；landing 頁保留（Leonard 揀）。

### 待辦 lesson（§8 monitoring）
派生產物（guidelines.json ← registry）手動脫鈎必 drift；正解 = generator + DOC_SYNC 登記「源頭變→重生」。呼應 playbook `derived-artifact-resync-on-source-change`。recurrence（其他派生 JSON）即 §8b promote。

### round-2 — Landing-page curate（agent-team 分工 + 審核；139→148）
- **Trigger:** Leonard 追問 round-1 保留嘅 16 個「課程文件目錄頁」可否 resolve 成真文件。
- **可行性實證:** 主 agent 爬 16 頁（egress；sub-agent egress 被 deny per S138）= 159 連結 → 真‧淨增益僅 ~9 份（71 dup + 77 雜訊：語言版本/分章 PDF/海報/通函附件/2009 過時報告）。
- **Agent-team（Agent tool，非 Workflow）:** 3 curation agent 並行分組（大目錄/KLA/跨KLA+area，純 local 無 egress）判 KEEP/DUP/NOISE → 8 KEEP；1 audit agent 對抗覆核 → 8/8 確認 0 降級 + 揪 2 漏網 + 立規則 R-DOC（HTML 目錄頁 vs 全文 PDF）+ grep 把「ph_pri 3 通告 url 錯」claim 收窄為 1/3。
- **主 agent egress 複核（sub-agent 做唔到，揪 2 錯）:** 逐份 HEAD + 開 PDF 抽真 title → 揪正 ma pmc/jsmc/ssmc 唔係「課程指引」係「數學KLA指引補充文件—學習內容」；agent 重組嘅 apl url 404、真 url 含 `&`；Suppl_guide year 抽唔到。
- **CHANGE（app.html GUIDELINES_REGISTRY）:** 加 9 entry（cle_kla_guide_2017 / chi_pri_lo_2023 / chi_sec_lo_2021 / pth_guide_2017 / pshe_kla_guide_2017 / ma_pri+jss+sss_content_2017 / apl_ca_guide_2017，全 HEAD-200 + 首頁驗證、category=課程）+ **修 3 data bug**（sci_kla_guide_2017 url 指錯 pshe 頁→science SEKLACG PDF+format / edbc20+edbc9 format HTML→PDF / edbc197 url=index.html→EDBCM_197_2024_C.pdf+format）。registry 148→**157**。
- **QC:** build_guidelines.py --self-test PASS（registry=157 public=148 dropped=9）；--check 139→148（curriculum 桶 123→132、回歸守衛 **-0 lost**）；9 新 id 全入 output；sci_kla/edbc197 修正生效；0 非 PDF/HTML leaked；版本 2.3.0→2.4.0。
- **held（未加）:** `Suppl_guide`（非華語補充指引全文 PDF）— year 不明 + g09 已覆蓋主題，列待人核（blank-over-wrong-guess）。
- **lesson:** landing 目錄頁 resolve = 大量 dup/雜訊、真增益細；正路 = 揀真文件加 registry（generator 自動帶入），唔係爬晒塞 json。sub-agent egress deny → egress 主 agent 做、curation/audit 純 local 分工。verify-don't-trust 再中（agent 估 url/title 兩度錯，egress 逐份核救返）。

### round-3 — 公積金覆蓋（Leonard 指定；148→152）
- **Trigger:** Leonard 問「公積金條例有冇包在此文件內」。
- **多層查證:** 標題層（guidelines.json/registry 157/Channel A）= **0 公積金 entry**；內文層 = 學校行政手冊 sag_2025_11/g24 各 **81 處**（引《教育條例》85條 / 《強制性公積金計劃條例》/ 《津貼·補助學校公積金規則》）+ coa_imc 2 / g04 2；**live Channel B 查「公積金」= synthesis + 8 results 帶頁碼**（用戶本來就搜到，TOP=g24 公積金帳目段）。
- **Leonard 指定加** EDB 公積金 hub url（`.../about-sch-staff/provident-fund/index.html`）→ 主 agent 爬：hub 底下 ~90 PDF 多數係季度 financial bulletin / 年報 / 2008-09 舊消息（非指引），真‧指引/條例類得幾份。
- **CHANGE（app.html registry +4，全 category=人力資源/hr，HEAD-200 + PDF 首頁驗證）:** provident_fund（hub HTML）/ sspf_general_info_2023（《津貼學校公積金的一般資料》16p）/ gspf_general_info_2023（《補助學校公積金的一般資料》14p）/ pf_edu_ord_2013_faq（《2013年教育(修訂)條例》相關常見問題 2p＝直接答「條例」）。registry 157→**161**。
- **QC:** self-test PASS（registry=161 public=152 dropped=9）；--check 148→152（hr 桶 2→6、回歸守衛 -0 lost）；4 公積金 id 全入 hr 桶；版本 2.4.0→2.5.0；0 非 PDF/HTML leaked。0 Supabase/backend/knowledge mutation。
- **lesson:** 「內容有冇覆蓋」要分標題層 vs 內文層查 + live Channel B 實證（內文搜尋本來 cover、標題層 0）；主題 hub 頁底下多數係數據/報告噪音，揀官方「一般資料 + 條例 FAQ」最有效。

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

⚠️ 然後讀 dev/HANDOFF_PACKAGE.md（可信狀態快照）。起手務必自行 verify git HEAD + knowledge.json._meta.stats vs SESSION_HANDOFF Current Baseline，並實測 egress（onrender /health，勿照抄）。S135-S140 證實 EDB + onrender + Supabase egress 均通；仍每次自測。

⚠️ Repo root = "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"（路徑含空格，shell 必須雙引號絕對路徑）。`python` 唔存在用 `python3`。git commit+push 由 Claude 做（指定檔勿 -A）。Agent team 係預設模式。回覆用中文。

S140 (2026-06-03)：**公開 guidelines.json 39→152（全集投影 + landing-curate +9 + 修 3 bug + 公積金 +4）完成、push live、QC 全 PASS**。HEAD origin/main 起手自行 verify（S140 closeout commit）。
- round-1：公開端點由 39 精選子集 → registry 全集投影 **139**（純規則剔 9 非文件：7 stat + 1 DOCX + 1 壞 URL religious_edu_jss）。
- round-2：**landing-curate** — agent-team（3 curate + 1 audit）+ 主 agent egress 逐份核實，由 16 課程文件目錄頁 159 連結揀 9 真‧KLA/課程指引全文 PDF 加入 registry + 修 3 registry data bug（sci_kla url 指錯頁→science PDF / edbc20+edbc9 format / edbc197 url=index→PDF）。公開 139→**148**（curriculum 桶 132）。
- round-3：**公積金覆蓋**（Leonard 指定）— 標題層之前 0 公積金（但內文層 sag/g24 已 cover、Channel B 搜到）→ 加 4 entry（provident_fund hub + sspf/gspf 一般資料 Q&A + 2013教育修訂條例 FAQ，category=人力資源/hr）。公開 148→**152**（hr 桶 2→6）。registry → **161**、版本 2.2.0→**2.5.0**。
- NEW generator `dev/build_guidelines.py`（registry=SSOT）：**日後 registry 加文件 → re-run `python3 dev/build_guidelines.py --write` 即同步，勿手寫 guidelines.json**（DOC_SYNC 已登記）。
- **held 待人核**：`Suppl_guide`（非華語補充指引全文 PDF）year 不明 + g09 主題重疊，暫不加。
- round-2 有改 app.html（registry data）；0 Supabase/backend/knowledge.json mutation。

Current objective and progress state:
- Baseline 不變：Supabase ~9,912 / 103 marker-bearing / CB-3 ceiling ~88% / brand live。公開 guidelines.json 39→**152**（本 session 契約變更：139 收斂 + 9 landing-curate + 4 公積金）；registry 161 entries。0 outstanding bug。

Pending tasks in priority order:
1. **下一階段方向（待 Leonard 明示）**：g14 資優+sen_curr_area+gifted_policy_docs 仍 0 Supabase chunks（SEN-adjacent，可補 g10/g19 §E.12 pattern）/ Q4 對外契約收斂（3 選項、敏感、未明示勿掂）/ §8b rule 2 automation。
2. **觀察（非阻塞）**：freshness scheduled 週跑（週一 09:00 UTC）開 freshness-change Issue；57014 cold-start mask；**knowledge.json._meta.stats.guidelines=39 follow-up**（升 152 與否，獨立 data-touch）；**`Suppl_guide` 非華語補充指引 PDF held 待人核**（year + g09 重疊）。
3. 既有 deferred：§E.10(a) ACCEPTED conditional / FAIL-A record-only / stat_fact 2025/26 ROI≈0 / HKEAA。

Key files changed this session:
- NEW dev/build_guidelines.py；guidelines.json(39→152)；**app.html(round-2 GUIDELINES_REGISTRY +9 + 修 4 行 data bug；round-3 +4 公積金 entry，148→161)**；K1_API_SPEC.md+dev/K1_API_SPEC.md；README.md；PMS §B.1·§F.9；CODEBASE_CONTEXT；DOC_SYNC_CHECKLIST；SESSION_HANDOFF/LOG。

Known risks / blockers / cautions:
- 🟢 0 outstanding bug。guidelines 擴張屬純加法（現有 39 條 0 lost、可 git revert）。
- 既有不變: 🔴 57014 transient(S139 backend retry；exhaust 後仍 400); FAIL-A(record-only); §E.10(a) ACCEPTED conditional; q.html/A·AB dormant 勿清; Q4 deferred 未明示勿掂; Stage-2 closed 勿復活; egress 每次自測; 路徑空格雙引號; wiki_chunks 欄名 `text` 非 `content`; guidelines.json 勿手寫(用 build_guidelines.py); 改 Draft code/data commit 必入 SESSION_LOG; init_backup gitignored。

Validation status:
- build_guidelines.py --self-test PASS（含回歸守衛）/ JSON valid / Circular 篩選範例 work / idempotent / 0 leak。
- Post-publish：GitHub Pages guidelines.json live = 152（起手可 curl 複驗；自訂域 policychecker.wongfu.net）。

Post-startup first action: 完成 §1 + HANDOFF_PACKAGE 起手序 + 自測（git HEAD / knowledge facts 455 / onrender /health / egress）+ lazy-query playbook INDEX 後，問 Leonard 下一階段方向（g14+gifted SEN 補完 / Q4 契約〔敏感未明示勿掂〕/ §8b automation）。可順手 curl 複驗 guidelines.json live=152 + 睇 GitHub 有冇 freshness-change Issue。未 Leonard 明示前唔好自行掂 Q4 / reopen §E.10 / 動 Stage-2 / 手寫 guidelines.json。
```

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
