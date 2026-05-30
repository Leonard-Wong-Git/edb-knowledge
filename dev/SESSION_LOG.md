# Session Log

<!-- Archives: dev/archive/ — entries moved when >400 lines or oldest entry >30 days -->

## 2026-05-30 Session 134 — Phase 3a #2 batch diagnostic = 5 sources no-op (429-masquerade-as-data near-miss)

- **ID:** Claude_20260530_1500
- **Trigger:** Leonard 起手 `/goal 1` 揀 Phase 3a #2 source case-by-case → 跑 5 候選 (tech_kla / chi_hist / ls_jss / arts / econ) 4-step diagnostic → 中途揀「行 ls_jss page-carry」→ 數據修正後 page-carry 撤回 → 全部「No-op + 文檔化 收尾」
- **§3 Risk:** Diagnostic READ-only = LOW；remediation (rejected) HIGH backend routing；ls_jss page-carry (rejected after data correction) = HIGH **避免咗**

### Diagnostic data (read-only：live onrender `/api/search/channel-b` + Supabase service-role REST count)

Supabase grand total = **9,713** (對齊 baseline)。Per-source chunk count（真實值，已濾走 429）：

| Cluster | Chunk counts | Live smoke 結論 |
|---|---|---|
| tech_kla | tech_kla_guide_2017 **237** / ict_2021 81 / ict_2007 135 / dat_2007 103 / ct_prog 10 / dat_supp 5 = **571** (5.88%) | 資訊/設計/編程 query → 對應 specific source + 頁碼正確；廣義「科技教育課程指引」semantic 撞 ma_kla/pri_science（非 top-1 wrong-domain）|
| chi_hist | chi_hist_jss_2019 **111** / sss 166 / ncs 25 / bilingual 33；history_sss 155；**history_jss_2019 = 0**（西史初中未入庫，獨立 gap）| 中史 query → chi_hist_jss_2019 top-3 p=8/1/29，零西史污染 |
| ls_jss | ls_jss_2010 = **251** | 「生活與社會中一至中三」→ ls_jss top-3 **p=78/8/76**；「生活與社會課程指引」→ 較新人文科 ph_pri_guide_2025 上（合理 supersede）|
| arts | arts_kla_guide_2017 **116** / music_p1_s6 85 / va_p1_s6 71 / music_sss_2024 69 / music_sss_2015 129 / va_sss_2015 144 = **617** | 「藝術教育學習領域課程指引」→ music_p1_s6_2024 #1 / va_p1_s6 #2-4 / pe_kla #5；**arts_kla_guide_2017 跌出 top-5** |
| econ | econ_2025 87 / supp_2025 32 / econ_2007 112 / supp_2015 31 = **262** | 限速截斷未完整 smoke；counts 確認 2025 版已入庫；pre-throttle partial 顯示最新版 dominate |

### CRITICAL CORRECTION — 429 masquerade-as-data near-miss

- 初步診斷以 ls_jss = **24 chunks / 0 pages** → 推「page-carry 需要」→ Leonard 授權執行。**呢個結論係錯。**
- 真相：HTTP **429 (onrender 10 req/min/IP + Supabase free-tier throttle)** 被我 diagnostic script 把錯誤 response 印成 `0` / `ERR` / 空白頁；加上 harness 把大批 parallel call buffer 後一次過 flush，造成「工具壞咗」嘅錯覺。**工具一直正常。**
- 正確：ls_jss_2010 = **251 chunks、已 page-carried**、live smoke top-3 帶頁碼。**page-carry 完全唔使做。**
- **因 STOP 咗冇執行** → 避免咗對**已經正確**嘅數據跑一次冇必要嘅破壞性 Supabase DELETE/INSERT mutation。

### Classification — all 5 = no-op (Leonard 揀)

- tech_kla / chi_hist / ls_jss / econ = **healthy**（topical query 正確 surface + 頁碼；data 充足）
- arts = **輕微 ranking 競爭**（arts_kla_guide_2017 完整書名 query 被較新 2024 音樂/視藝分科指引壓出 top-5，同 S122/S123 music_sss_2024 KLA-vs-分科 pattern 一致）→ Leonard 裁示視為**可接受 newer-guide-優先**、no-op（強推 arts_kla 上反而壓低更有用嘅分科指引，同 g29 quota-cap 反效果同理）
- Phase 3a #2 清單 5 源全 close as false-alarm/no-op

### Lessons

- **§G.2 verify-don't-trust 延伸（5th-instance candidate）**：Throttled/rate-limited API response 會**偽裝成數據**（0 count / 空白頁 / ERR），導致假「需要修」結論。Diagnostic script 必須 distinguish HTTP 429/error vs 真 0；live smoke 對 onrender 要 pacing（10 req/min/IP）。§8 monitoring tier — near-miss 非 incident、未升 SOP（promote 入 PMS §G.2 banner 留下次評估）。
- 「Ranking competition」listed-in-backlog 多源自 S122-S125 generic batch-smoke 非-surface 觀察；topical query 一驗即知 4/5 健康（同 g29/S133 meta-lesson 一致）。

### Sources changed in this session

- `dev/SESSION_HANDOFF.md`（Open Priority #1 Phase 3a #2 5 源剔走 + ✅ S134 entry + Last/Previous demote）
- `dev/SESSION_LOG.md`（本 S134 entry prepend）
- temp diagnostic helpers（`dev/_phase3a_smoke.py` / `dev/_phase3a_count.py` / `dev/_dump.py` / `dev/_dump2.py`）已刪
- **NOT modified:** code / data / Supabase / source_registry / knowledge.json / app.html / backend / PROJECT_MASTER_SPEC / CODEBASE_CONTEXT

### DOC_SYNC Matrix Scan

| Change Category | Required Doc Updates | Status |
|---|---|---|
| Phase 3a diagnostic finding (no-op closure ×5) | SESSION_HANDOFF Open Priority #1 + ✅ S134 entry | ✓ Done |
| Session history | SESSION_LOG S134 entry | ✓ Done |
| New process lesson (429-masquerade) | SESSION_LOG Lessons + handoff caution; PMS §G.2 promote deferred | ✓ Done (monitoring tier) |
| No code / data / config / external service change | (no doc impact) | N/A |

(Registry `dev/DOC_SYNC_CHECKLIST.md` not consulted directly — pure read-only diagnostic finding closure, no governance-doc category row applies beyond §4 PERSIST baseline.)

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

⚠️ 然後讀 dev/HANDOFF_PACKAGE.md（可信狀態快照）。起手務必自行 verify git HEAD + knowledge.json._meta.stats vs SESSION_HANDOFF Current Baseline，並實測 egress（onrender /health，勿照抄）。

⚠️ Repo root = "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"（路徑含空格，shell 必須雙引號絕對路徑）。`python` 唔存在用 `python3`。git commit+push 由 Claude 做（指定檔勿 -A）。Agent team 係預設模式。回覆用中文。

S134 (2026-05-30, Leonard /goal 1 揀 Phase 3a #2 → 跑 5 源 4-step diagnostic → 全部 No-op + 文檔化 收尾)：**Phase 3a #2 batch (tech_kla / chi_hist / ls_jss / arts / econ) = 5 源全 no-op, 0 code/data/Supabase mutation**。

⚠️ KEY LESSON S134 (§G.2 延伸): 診斷中途因 HTTP 429 (onrender 10 req/min + Supabase throttle) 被 script 印成 0/ERR/空白頁 → 誤判 ls_jss = 24 chunks/0 pages 需要 page-carry。STOP 後修正：ls_jss 真實 = 251 chunks 已 page-carried、healthy。**Throttled API response 會偽裝成數據；live smoke 必須 pace (10 req/min) + distinguish 429 vs 真 0。** 差啲對正確數據跑冇必要破壞性 Supabase mutation。

Diagnostic 真實數據 (429 已濾): tech_kla cluster 571 (tech_kla 237) / chi_hist 中史 277 (history_jss_2019=0 西史初中 gap) / ls_jss 251 page-carried / arts cluster 617 (arts_kla 116) / econ 2025版 119+舊143。Live smoke: 4/5 topical query 正確 surface + 頁碼。

Classification: tech_kla/chi_hist/ls_jss/econ = healthy no-op；arts = 輕微 ranking 競爭 (arts_kla_guide_2017 完整書名被 2024 分科音樂/視藝指引壓出 top-5)，Leonard 裁示視為可接受 newer-guide-優先 no-op (強推反壓低有用分科指引，同 g29 quota-cap 反效果同理)。

Current objective and progress state:
- Baseline unchanged: Supabase 9,713 / 100/113 marker-bearing / CB-3 final ceiling ~88% / brand launch live (policychecker.wongfu.net)
- S134 = pure governance doc update, 0 code/data/Supabase mutation
- Phase 3a 清單剩 ~9-12 sources (5 源再剔走)

Pending tasks in priority order:
1. **Phase 3a #3 剩餘源 case-by-case** (geog / history_jss_2019=0 西史初中 coverage gap / dat / ict / pe / music_sss / 等)。沿用 S133 4-step diagnostic template + S134 教訓 (pace live smoke、429 vs 真 0)。Each source individual judgment。注意 history_jss_2019=0 chunks = 真 coverage gap (非 ranking)。
2. **Phase 3c 5 HTML catalogue-level refresh (low ROI)**: stat_edb_figures / arts_curr_docs / ph_pri_curr / edbc197_2024_ph_pri / moral_civic_curr。結構天花板。
3. **既有 deferred backlog**: §E.10 conditional ACCEPTED / 57014 transient / FAIL-A record-only / P2/P3 (39→148) / Mobile UI P2 / HKEAA / stat_fact upgrade (deprioritized)
4. **Q4 對外契約收斂** (deferred; 未明示勿掂)
5. **§8b rule 2 automation tooling** (future) + **PMS §G.2 5th-instance (429-masquerade) promote 評估**

Key files changed this session:
- `dev/SESSION_HANDOFF.md` (Open Priority #1 5 源剔走 + ✅ S134 + Last/Previous demote)
- `dev/SESSION_LOG.md` (S134 entry prepend + 4-step diagnostic + 429 correction + verbatim handoff)
- temp diagnostic helpers 已刪
- **NOT modified**: 任何 code / data / Supabase / source_registry / knowledge.json / app.html / backend / PMS / CODEBASE_CONTEXT

Known risks / blockers / cautions:
- 0 new product risks (diagnostic-only session)
- NEW process caution: onrender backend 10 req/min/IP rate limit + Supabase free-tier throttle → diagnostic live smoke 必須 pace + 處理 429（勿當數據）
- 既有 risks 不變: 🔴 Supabase 57014 transient (retry); FAIL-A 注入 regression (record-only); §E.10 (a) ACCEPTED conditional; q.html/A·AB code path/backend dormant 勿清; Q4 deferred 未明示勿掂; Stage-2 closed 勿復活
- egress 每次自測; EDB PDF `url_primary` (§E.12); 路徑空格雙引號; Testing/ 喺 Draft git 外; 改 Draft code/data commit 必入 SESSION_LOG (本 session 0 code/data 改、僅 2 governance doc)

Validation status:
- PASS S134 §3d diagnostic scenarios (chunk count via service-role REST / live smoke 4/5 topical queries 正確 + 頁碼 / 429 correction verified)
- COMMIT: S134 doc commit pending (起手自行 verify HEAD)
- OPEN: Phase 3a #3 剩餘源 / 3c / 既有 deferred backlog

Post-startup first action: 完成 §1 + HANDOFF_PACKAGE 起手序 + 自測 (git HEAD / knowledge.json._meta.stats facts:455 / Supabase 9,713 / egress onrender /health warm 455) 後，**S134 Phase 3a #2 batch 5 源 no-op closed**。第一件事＝問 Leonard 揀: (a) **Phase 3a #3 剩餘源** (geog / history_jss gap / dat / ict / pe / music_sss — 4-step diagnostic + pace live smoke 防 429); (b) **Phase 3c 5 HTML refresh** (low ROI); (c) **既有 deferred backlog**; (d) **Q4 契約** (未明示勿掂); (e) 收工？未 Leonard 明示前**唔好自行 resume / 掂 Q4 契約 / reopen §E.10**。
```

---

## 2026-05-28 Session 133 — Phase 3a #1 g29 dominance diagnostic = false-alarm (data scarcity, no-op)

- **ID:** Claude_20260528_1339
- **Trigger:** Leonard 起手揀 Phase 3a batch ranking polish → 揀第一個 target = g29 KGECG-TC-2017 dominance → 提出 hypothesis「可能本身有關幼稚園的資料就不多」→ empirical verify
- **§3 Risk:** Diagnostic READ-only = LOW; if remediation applied → HIGH (backend routing). Leonard 揀「No-op + 文檔化」→ 全程 LOW (doc-only)

### Diagnostic data (3 tasks, all read-only)

- **Task #1 — Inventory (source_registry):** 151 total → KG-related 4 sources only: `g29` 幼稚園教育課程指引 2017 主框架 / `g25` 幼稚園相關指引及須知 / `g26` 2026/27 收生安排 / `stat_kg` 統計數字 (Channel B filter `content_type!=="stat_fact"` 排除). **User-facing 只 3 個 KG sources.**
- **Task #2 — Supabase chunk count per KG source:** g29=**107** / g26=19 / g25=1 / stat_kg=8. KG user-facing total = **127 chunks**. g29 占 KG 庫 **84.3%**. KG 占全 Supabase 9,713 = **1.3%**.
- **Task #3 — Live smoke 5 KG queries via `/api/search/channel-b`** (top-5 distribution):

  | Query | Top-1~5 source distribution | g29 in top-5 | 評估 |
  |---|---|---|---|
  | 幼稚園課程框架 | g29 / g29 / g29 / pri_curr_guide_2024 / music_p1_s6_2024 | 3/5 | ✅ 合理（課程框架=g29 核心 topic）|
  | 幼稚園收生 | g26 / g26 / g26 / — / — | 0/3 | ✅ g26 正確 dominate；g29 不沾邊 |
  | 幼稚園評估 | g29 / pri_curr_guide_2024 / g29 / g29 / va_p1_s6_2024 | 3/5 | ✅ g29 合理（評估=g29 ch.4 內容）|
  | 幼稚園教師專業發展 | g06 / role_facts_hr / g06 / g06 / sag_2025_11 | **0/5** | ✅ CPD 領域 g06 正確；g29 完全 yield |
  | 幼稚園教學語言 | g29 / g29 / g29 / chi_pri_guide_2023 / chi_pri_guide_2023 | 3/5 | ✅ g29 合理（教學語言=g29 內容）|

### Diagnostic conclusion

- **Root cause = (b) data scarcity reflection** — KG domain 結構性內容貧瘠（only 3 user-facing sources, 127 chunks），g29 結構性 own 84% 嘅 KG content
- **NOT (a) ranking bug** — g29 唔係盲目 dominate: admission queries g26 上、CPD queries g06 上、g29 完全 yield；只喺 curriculum/teaching/assessment 即 g29 核心 topic 上 dominate（合理）
- **Cross-domain contamination** 次要觀察: `pri_curr_guide_2024` / `music_p1_s6_2024` / `va_p1_s6_2024` 喺 KG queries surface top-4/5 — embedding semantic similarity，唔搶 top-1~3、user-visible harm 微

### Fix decision (Leonard 揀)

- **No-op + 文檔化** — 0 code/data/Supabase mutation
- Rationale: quota cap 會將 g29 從 top-5 踢走、留空位俾跨域非-KG sources surface，反而傷北極星 traceability。**唯一相關 KG 主文件被搶位 = 比 g29 結構性 dominate 更差**
- Phase 3a #1 closed as false-alarm

### Lessons (§G.2 verify-don't-trust hypothesis 再應用)

- 「Dominance」唔等於「Ranking bug」— 必須 first 量 inventory + chunk count + live smoke 確認 alternative source 存在與否
- Future Phase 3a sources 診斷模板：(1) registry inventory (2) Supabase chunk distribution (3) live smoke 4-5 representative queries (4) judge root cause class
- 適用 §8 monitoring tier — 此次 false-alarm 唔升 SOP，但記錄入 process knowledge

### Sources changed in this session

- `dev/SESSION_HANDOFF.md` (Open Priority #1 g29 剔走 + ✅ S133 完成 entry prepend)
- `dev/SESSION_LOG.md` (本 S133 entry prepend)
- **NOT modified:** code / data / Supabase / source_registry / knowledge.json / app.html / backend / PROJECT_MASTER_SPEC / CODEBASE_CONTEXT

### DOC_SYNC Matrix Scan

| Change Category | Required Doc Updates | Status |
|---|---|---|
| Phase 3a diagnostic finding (false-alarm closure) | SESSION_HANDOFF Open Priority #1 + ✅ S133 entry | ✓ Done |
| Session history | SESSION_LOG S133 entry | ✓ Done |
| No code / data / config / external service change | (no doc impact) | N/A |

(Registry `dev/DOC_SYNC_CHECKLIST.md` not consulted directly — no governance-doc category rows match a pure read-only diagnostic finding closure. Doc updates above are §4 PERSIST baseline minimum.)

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

⚠️ 然後讀 dev/HANDOFF_PACKAGE.md（可信狀態快照）。起手務必自行 verify git HEAD + knowledge.json._meta.stats vs SESSION_HANDOFF Current Baseline，並實測 egress（onrender /health，勿照抄）。

⚠️ Repo root = "/Users/leonard/Downloads/Claude Project/Claude-edb-knowledge/Draft"（路徑含空格，shell 必須雙引號絕對路徑）。`python` 唔存在用 `python3`。git commit+push 由 Claude 做（指定檔勿 -A）。Agent team 係預設模式。回覆用中文。

S133 (2026-05-28, Leonard 起手揀 Phase 3a #1 g29 dominance → 提出 hypothesis「幼稚園資料本身少」→ empirical verify → no-op + 文檔化 → 收工)：**Phase 3a #1 g29 dominance diagnostic = false-alarm, no code/data/Supabase mutation**。HEAD origin/main = `8d9aa54` (S133 closeout)。

Diagnostic data (4-step read-only template, future Phase 3a 沿用):
1. Registry inventory: 151 sources → 4 KG-related (g29 / g25 / g26 / stat_kg), user-facing 只 3 (stat_kg `content_type=stat_fact` 被 Channel B filter 排除)
2. Supabase chunk count per KG source: g29=**107** (KG 庫 84.3%) / g26=19 / g25=1 / stat_kg=8；KG user-facing total 127 = 全庫 9,713 之 **1.3%**
3. Live smoke 5 queries top-5: 幼稚園收生→g26 #1+#2+#3 (g29 完全不出) / 幼稚園教師專業發展→g06 #1+#3+#4 (g29 完全 yield) / 幼稚園課程框架/評估/教學語言→g29 dominate (合理、g29 核心 topic)
4. Classification: **(b) data scarcity NOT (a) ranking bug**

Fix decision per Leonard: **No-op + 文檔化**。Rationale: quota cap 會將 g29 從 top-5 踢走、留空位俾跨域非-KG sources surface，反而傷北極星 traceability（唯一相關 KG 主文件被搶位 = 比結構性 dominate 更差）。Phase 3a #1 closed as false-alarm。

Lesson (§G.2 verify-don't-trust hypothesis 再應用): 「Dominance」 ≠「Ranking bug」— 必先量 inventory + chunk count + live smoke 確認 alternative source 存在與否。Future Phase 3a 沿用 4-step diagnostic 模板。§8 monitoring tier, 未升 SOP。

Current objective and progress state:
- S132 base unchanged: Supabase 9,713 / 100/113 marker-bearing / CB-3 final ceiling ~88% / brand launch live (policychecker.wongfu.net)
- S133 = pure governance doc update, 0 code/data/Supabase mutation
- Phase 3a 清單剩 ~14-17 sources (g29 剔走)

Pending tasks in priority order:
1. **Phase 3a #2 source case-by-case**: tech_kla / chi_hist / ls_jss / arts ranking competition / econ_sss_supp competition / 等。Future sources 沿用 S133 4-step diagnostic template。Each source needs individual judgment (dedicated route / query expansion / per-source quota / OR no-op if data-scarcity-confirmed)。
2. **Phase 3c 5 HTML catalogue-level refresh (low ROI)**: stat_edb_figures (vault mojibake) / arts_curr_docs / ph_pri_curr / edbc197_2024_ph_pri / moral_civic_curr。結構天花板。
3. **既有 deferred backlog**: §E.10 conditional ACCEPTED / 57014 transient / FAIL-A record-only / P2/P3 (39→148) / Mobile UI P2 / HKEAA / stat_fact upgrade (deprioritized)
4. **Q4 對外契約收斂** (deferred; 未明示勿掂)
5. **§8b rule 2 automation tooling** (future; KLA-title embedding similarity check sub-agent prompt)

Key files changed this session:
- `dev/SESSION_HANDOFF.md` (Open Priority #1 g29 剔走 + ✅ S133 prepend + Last/Previous demote)
- `dev/SESSION_LOG.md` (S133 entry prepend with 4-step diagnostic + DOC_SYNC + verbatim handoff)
- **NOT modified**: 任何 code / data / Supabase / source_registry / knowledge.json / app.html / backend / PROJECT_MASTER_SPEC / CODEBASE_CONTEXT (read-only diagnostic only)

Known risks / blockers / cautions:
- 0 new risks (diagnostic-only session)
- 既有 risks 不變: 🔴 Supabase free-tier 57014 transient (retry 即恢復); FAIL-A 注入 regression (record-only); §3c FAIL-A/B record-only; §E.10 (a) ACCEPTED conditional on cosmetic-gate design unchanged; q.html/A·AB code path/backend `/channel-a`·`/combined` endpoint dormant 勿清; Q4 deferred 未明示勿掂; Stage-2 closed 勿復活
- egress 每次自測; EDB PDF 永遠用 `url_primary` (§E.12); 路徑空格雙引號; Testing/ 喺 Draft git 外; 改 Draft code/data commit 必入 SESSION_LOG (本 session 0 code/data 改、僅 2 governance doc)

Validation status:
- PASS S133 §3d 3 scenarios (inventory query / Supabase count query / live smoke 5 queries)
- COMMITTED: S133 doc commit `8d9aa54` (origin/main advanced from `93a3b74`)
- OPEN: Phase 3a #2 / 3c / 既有 deferred backlog

Post-startup first action: 完成 §1 + HANDOFF_PACKAGE 起手序 + 自測 (git HEAD 對齊 SESSION_HANDOFF Last entry / knowledge.json._meta.stats facts:455 / Supabase chunk count = 9,713 / egress onrender /health warm 455) 後，**S133 Phase 3a #1 g29 false-alarm closed**。第一件事＝問 Leonard 揀: (a) **Phase 3a #2 source** (tech_kla / chi_hist / ls_jss / arts / econ_sss_supp — case-by-case 4-step diagnostic); (b) **Phase 3c 5 HTML catalogue-level refresh** (low ROI); (c) **既有 deferred backlog**; (d) **Q4 對外契約收斂** (未明示勿掂); (e) 收工？未 Leonard 明示前**唔好自行 resume / 掂 Q4 契約 / reopen §E.10**。
```

---
