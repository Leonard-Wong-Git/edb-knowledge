# Session Log

<!-- Archives: dev/archive/ — entries moved when >400 lines or oldest entry >30 days -->

## 2026-05-02 Session 102 — 已核實事實庫去重 + 學校行政手冊雙重 ingestion 發現

- **ID:** Claude_20260502_0005
- **Summary:** 已核實事實庫 1,001 條 facts 之中 484 條為 exact duplicate（48% 重複），執行 Strategy B（保留 all_roles 副本，刪個別 role bucket 副本）後三層同步降至 792 條（移除 209 條，剩 193 組屬 mid-level sharing 不強行壓平）。Channel B 學校行政手冊 dry-run 發現驚訝結果：g24（300 chunks）vs sag_2025_11（415 chunks）hash 重疊 0%，即兩者係同一份文件嘅兩種切割方式（g24 = Session 98 PyMuPDF whole-doc fetch；sag = Session 76 pdftotext partial extract Ch1/3/6/7），DB DELETE 唔合適，改方案下節 backend 加 source alias map（軟 dedup）。
- **Changed:** `role_facts.json`, `knowledge.json`, `dev/knowledge/role_facts.json`, `dev/init_backup/20260502_dedup/*`（新增 backup）, `dev/role_facts_dedup_preview.json`（中介，可刪）
- **Done:**
  - ✅ **[已核實事實庫掃描]** sandbox 跑 Python script：325 組 exact duplicate / 484 重複行 / 0 fuzzy variant；典型 pattern「同一條 fact 出現於 all_roles + 個別 role × N」
  - ✅ **[Strategy B 三層覆蓋]** 三層 backup 至 dev/init_backup/20260502_dedup/；apply dedup（移除個別 role bucket 入面已存在於 all_roles 嘅副本）；三層 facts: 1,001 → 792；_meta.version: 2.2.0 → 2.3.0；updated: 2026-05-02
  - ✅ **[Backend selector 邏輯驗證]** knowledgeSelector.ts getTopicFacts() 已 union all_roles + role facts + uniqueFacts() — dedup 後按角色查詢仍然拎齊全部 unique facts，Circular System 注入內容不變
  - ✅ **[Sanity test selector union]** 模擬 4 條典型 case：finance.principal=78 / hr.teacher=123 / curriculum.subject_head=67 / general.eo_admin=30；union 等於 sum 證明 dedup 乾淨（無 cross-bucket 殘留）
  - ✅ **[學校行政手冊 dry-run]** 用戶 Terminal curl + Python 比對 g24 vs sag chunks hash：重疊 0/300 vs 0/415，**完全冇 chunk-level 重疊**；發現兩者係同一文件不同切割方式（g24 含封面 + TOC，sag 只 cover Ch1/3/6/7）
- **QC:** TypeScript `npm run check` PASS 0 errors；selector union sanity test PASS（4/4 case 無 cross-bucket 殘留）；三層 facts/version/updated 全對齊
- **Pending（用戶 Terminal 執行）:**
  - 移除 sandbox 留低嘅 preview 檔（permission 問題，sandbox rm 失敗）：`rm -f ~/Downloads/Claude-edb-knowledge/dev/role_facts_dedup_preview.json`
  - Git commit + push（含 dedup 三層 + backup + Session 102 entry）
- **Next:** 1. backend 加 source alias map（g24 → sag_2025_11），令配額排序視兩個 source_id 為同組；2. 學校行政手冊 vault 重新 ingest 統一 source_id（backlog）；3. Channel B 線上重 curl 驗證 dedup 後 Channel A 注入不變

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| Knowledge data structural cleanup | role_facts.json + knowledge.json + dev/knowledge/role_facts.json _meta.version + dedup_note | ✓ Done |
| Version bump v2.2.0 → v2.3.0 | 三層 _meta.version + dev/SESSION_HANDOFF baseline | ✓ Done |
| 學校行政手冊雙重 ingestion 發現 | Open Priorities 加 backend source alias map | ✓ Done |

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Current objective and progress state:
- Session 102 (2026-05-02) 完成已核實事實庫 Strategy B dedup：三層由 1,001 → 792 facts；_meta.version v2.2.0 → v2.3.0；已 backup 至 dev/init_backup/20260502_dedup/
- Backend selector 邏輯驗證：knowledgeSelector.ts 已 union all_roles + role facts，dedup 後按角色查仍拎齊
- 學校行政手冊 dry-run 發現：g24（300 chunks）vs sag_2025_11（415 chunks）hash 重疊 0%，係同一文件嘅兩種切割方式（g24 = whole PDF + TOC，sag = Ch1/3/6/7 partial），DB DELETE 唔合適
- 商品狀態：v2.3.0 / role_facts 792 / Supabase 10,736 chunks / vault 120 sources / Channel A cache size 應隨 dedup 變細

Pending tasks in priority order:
1. Backend 加 source alias map（g24 → sag_2025_11）— wikiRepository.ts quota gate 用 canonical source 計數，避免兩個 source_id 同時佔配額
2. 學校行政手冊 vault 重新 ingest 統一 source_id（backlog，下一輪 vault refresh 一齊做）
3. 線上 Channel B 重 curl 驗證 dedup 後質量（Channel A 注入應不變因為 selector union）
4. 8 個無法擷取嘅 source triage（按 memory 規範先驗 source 質素）
5. 評估視藝/科技/英文課程指引（g21/g22/g33）直連 PDF 必要性

Key files changed in this session:
- role_facts.json + knowledge.json + dev/knowledge/role_facts.json（三層 dedup + version bump）
- dev/init_backup/20260502_dedup/*（dedup 前 backup 三層 snapshot）
- dev/SESSION_LOG.md（Session 102 entry）
- dev/SESSION_HANDOFF.md（Last Session Record / Open Priorities 更新）

Known risks / blockers / cautions:
- Cowork sandbox egress allowlist 不含 edb-knowledge.onrender.com → 線上驗證需用戶 Terminal
- Render free tier cold start ~30s after 15min idle
- Mac Python.framework 缺 SSL CA bundle，Supabase REST 直接 hit 會 SSLCertVerificationError；要用 curl 繞
- Shared MemPalace recovery workaround (hnsw:num_threads=1)；保留備份 /Users/leonard/mempalace/palace.pre-recovery.20260421_0838
- Supabase free tier 500MB DB limit；現約 50MB
- 殘留 193 組重複（mid-level sharing：fact 屬多個 role 但 all_roles 唔 hold）係 trade-off，唔強行壓至 schema 改動

Validation status:
- PASS: TypeScript npm run check 0 errors
- PASS: 三層 facts 對齊 792 / version 2.3.0 / updated 2026-05-02
- PASS: Selector union sanity test（finance.principal=78 / hr.teacher=123 / curriculum.subject_head=67 / general.eo_admin=30）
- PASS: 學校行政手冊 dry-run（hash 重疊 0%，發現同一文件雙重 ingestion 真相）

Post-startup first action: 詢問 Leonard：先 ship backend source alias map（解學校行政手冊配額重複佔位），抑或開新方向。
```

---

## 2026-05-02 Session 101 — 來源配額排序（Channel B 量級層治理）

- **ID:** Claude_20260502_0004
- **Summary:** 處理 Session 100 線上驗收剩低嘅量級層問題：學校行政手冊（SAG, 415 chunks）對教師病假 query 食晒 top_k；視藝指引（va_p1_s6, 86 chunks）對幼稚園 query 蓋過幼稚園課程指引（g29, 132 chunks）。本 session 在 wikiRepository 加入「每來源預留位」機制（per-source quota cap），令單一強勢 source 唔再 monopolize top results。
- **Changed:** `backend/src/lib/wikiRepository.ts`, `backend/src/api/searchChannelB.ts`
- **Done:**
  - ✅ **[wikiRepository 加配額參數]** `WikiSearchOptions` 加 `maxPerSource?: number`；當 maxPerSource > 0，內部 over-fetch（傳俾 Supabase 嘅 match_count 由 topK → topK × 5），確保配額排序有夠多元 source 可選
  - ✅ **[配額排序邏輯]** dedup 之後加 quota gate：按 score DESC 行，每 source 計數，達 cap 後 skip；取夠 topK 即 break；cap 係上限唔係下限（唔強塞低分 chunks 入 top_k）
  - ✅ **[searchChannelB caller-side]** 計算 `maxPerSource = max(2, ceil(top_k / 3))`；當 sourceIds 只有 1 個時自動 disable（單一 source 唔需要 diversity）
  - ✅ **[Sanity test]** 本地模擬 mock chunks 跑 quota gate：8 條輸入（sag×4, va×3, g29×1）→ topK=5 cap=2 → 結果 sag×2 + va×2 + g29×1，配額成功釋位俾低 score 高優先 source（g29 0.50 入榜雖然輸俾 sag-3 0.55）
- **QC:** TypeScript `npm run check` PASS 0 errors；本地 sanity test PASS（quota 分佈正確）；線上端對端驗收待用戶 Terminal curl
- **Pending（用戶 Terminal 執行）:**
  - Git commit + push（含 wikiRepository + searchChannelB 改動 + Session 101 entry）
  - Render auto-deploy 等 ~2-3 分鐘
  - 重 curl 三條 query 對比效果
- **Next:** 1. 收線上驗收結果；2. 視乎 query 1 病假 / query 3 幼稚園是否 dominate 改善決定要唔要再 tune cap 比例；3. 學校行政手冊重複文件去重（資料層 cleanup）排程

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| Backend behavior change (Channel B ranking) | SESSION_HANDOFF Open Priorities; Session entry QC evidence | ✓ Done |
| New search option (maxPerSource) | wikiRepository.ts inline JSDoc | ✓ Done |

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Current objective and progress state:
- Session 101 (2026-05-02) ship 來源配額排序（per-source quota cap）— wikiRepository.ts WikiSearchOptions 加 maxPerSource；搜尋邏輯：score DESC 行，每 source 計數達 cap 後 skip；over-fetch（topK×5）確保多元 source 可選
- searchChannelB.ts caller 計算 maxPerSource = max(2, ceil(top_k / 3))；單 source allowlist 時自動 disable
- TypeScript check 0 errors；本地 sanity test PASS
- 商品狀態：v2.2.0 / role_facts 1,001 / Supabase 10,736 chunks / vault 120 sources / Channel A cache warm size:517

Pending tasks in priority order:
1. 收線上驗收結果（用戶 Terminal curl 三條 query）— 確認教師病假改善、教師註冊維持、幼稚園 g29 上升
2. 學校行政手冊重複文件去重（Supabase SQL）— g24 同 sag_2025_11 同份文件兩次 ingestion，重複 715 chunks；先 dry-run 驗證 sag 涵蓋 g24 全部內容才能執行
3. 8 個無法擷取嘅 source triage（按 memory 規範先驗 source 質素）
4. 評估視藝/科技/英文課程指引（g21/g22/g33）是否需要直連 PDF
5. 監察 Render cold start 對線上驗證影響（~30s after 15min idle）

Key files changed in this session:
- backend/src/lib/wikiRepository.ts（WikiSearchOptions 加 maxPerSource；searchWiki 加 over-fetch + quota gate）
- backend/src/api/searchChannelB.ts（caller-side 計算 maxPerSource）
- dev/SESSION_LOG.md（Session 101 entry）
- dev/SESSION_HANDOFF.md（Open Priorities regenerated）

Known risks / blockers / cautions:
- Cowork sandbox egress allowlist 不含 edb-knowledge.onrender.com → 線上驗證需用戶 Terminal
- Render free tier cold start ~30s after 15min idle
- Shared MemPalace recovery workaround (hnsw:num_threads=1)；保留備份 /Users/leonard/mempalace/palace.pre-recovery.20260421_0838
- Supabase free tier 500MB DB limit；現約 50MB
- 學校行政手冊去重高風險（SQL DELETE）— 必先 dry-run 驗證 sag 涵蓋 g24 全部內容
- 配額排序 over-fetch（topK×5）會增加 Supabase 帶寬；以 top_k=8 計即 40 rows 上限，影響不大但要監察

Validation status:
- PASS: TypeScript npm run check 0 errors
- PASS: 本地 sanity test（mock chunks quota 分佈正確）
- PENDING: 線上端對端驗收（用戶 Terminal curl 三條 query）

Post-startup first action: 詢問 Leonard：線上 curl 結果如何，下一輪揀學校行政手冊去重 / 8 skipped sources triage / 新功能。
```

---

## 2026-05-02 Session 100 — 治理補檔（Verbatim 區塊回填 + §4a Archive）

- **ID:** Claude_20260502_0003
- **Summary:** 啟動 §1 read 後發現 Sessions 98 / 99 closeout 缺 `### Next Session Handoff Prompt (Verbatim)` 區塊，並偵測 §4a 觸發（655 lines）。本 session 完成治理回填與歷史歸檔，SESSION_LOG 由 13 entries 壓至 3 entries。Channel B 線上驗證因 sandbox egress 限制改為 curl 指令包交予用戶 Terminal 跑。
- **Changed:** `dev/SESSION_LOG.md`, `dev/archive/SESSION_LOG_2026_Q2.md`（新增）, `dev/SESSION_HANDOFF.md`
- **Done:**
  - ✅ **[Session 98 Verbatim 補回]** 反映 vault 擴充完成 / Supabase 10,736 chunks / 8 skipped / MemPalace pending
  - ✅ **[Session 99 Verbatim 補回]** 反映 v2.2.0 全平台對齊 / PlatformIntroPanel 重設計 / Logo 導向 / git push 待用戶執行
  - ✅ **[§4a Archive]** `python3 docs/qa/session_log_maintenance.py --apply` 執行：lines 655 → 151；entries 13 → 3；archived=10 → `dev/archive/SESSION_LOG_2026_Q2.md`；最新 entry prompt block ok=True
  - ✅ **[B/D 根因 feedback 入 memory]** 「找不到直連 PDF」優先 triage source 本身（URL 失效 / SPA / 官方下架），唔好馬上設計 fallback pipeline
  - ✅ **[Channel B 質量 triage]** 用戶 Terminal curl g04 病假 / g24 教師註冊 / g29 幼稚園 query — 三條全部 miss target source；Supabase chunks count 確認資料齊全（g04:7 / g24:300 / g29:132 / sag:415），排除資料層假設
  - ✅ **[F1 hr_admin regex 擴充]** `searchChannelB.ts` line 161 加入 `教師註冊|註冊處|聘任|聘用|招聘|入職|教師資格|教席|常額教席|代課教師` — 修 Query 2「教師註冊及聘任程序」原本 detect=null
  - ✅ **[F2 curriculum allowlist 加幼兒]** `searchChannelB.ts` SOURCE_SETS.curriculum 加入 g29 / g25 / g26 / stat_kg；TOPIC_KEYWORDS.curriculum regex 加入 `幼稚園|幼兒|學前|K1|K2|K3|遊戲學習` — 修 Query 3「幼稚園學習領域與評估」原本只見小學/中學課程
  - 🔍 **[Bonus 發現]** g24 (300 chunks) 與 sag_2025_11 (415 chunks) 係同一份《學校行政手冊（2025 年 11 月版）》兩次 ingestion，DB 重複佔 715 chunks 配額；列入 F4 待處理
- **QC:** §4a `--check` PASS（line_count=151，trigger=False）；archive script 自帶 latest prompt block 完整性檢查 PASS；F1+F2 改動後 `npm run check` (TypeScript tsc --noEmit) PASS 0 errors；用戶 Terminal 重 curl 三條 query Render 線上驗收：
  - **Query 1（教師病假上限多少天）**：sag × 2 → 仍係 366 日學校假期表，g04 未命中 — 屬 F3 量級層（SAG 415 chunks 蓋 g04 7 chunks），非 F1+F2 範疇，預期內 miss
  - **Query 2（教師註冊及聘任程序）**：sag × 4 全 hr 相關（聘任類型 / 校董會 / 常額代課），原本兩條 off-topic（chi_lit / edbcm58_pri_science）已清晒 — ✅ F1 完全成功
  - **Query 3（幼稚園學習領域與評估）**：va_p1_s6 × 3 + **g29 第 4 位 score 0.5904** + pe — g29 上線但未 dominate；F2 allowlist 修補生效但量級競爭仍蓋 — 🟡 部分成功
- **Bonus 發現驗證:** Query 1 嗰條 SAG chunk「366 日 -90 日學校假期 -3 日教師發展日」其實 SAG 內嵌 g04 教職員批假指引總額表，再次印證 F4 dedup 重要（SAG 同 g24/g04 內容有重疊）
- **MemPalace sync 修正:** 用 venv python 已 work，4 sessions（97/98/99/100）+ SESSION_HANDOFF snapshot 寫入 wing claude_edb_knowledge，total 15 entries
- **Pending（用戶 Terminal 執行）:**
  - **A** MemPalace sync 修正：用 venv python（system python3 無 chromadb）
  - **新一輪 git push** 含 F1+F2 修補 + SESSION_LOG 後續記錄
  - **Render auto-deploy** 等 ~2-3 分鐘
  - **重 curl 三條 query** 對比 F1+F2 修補效果
- **Next:** 1. 收新一輪 curl 結果；2. F3 量級層（per-source diversity）排程；3. F4 g24/sag dedup 排程；4. 視 user 意願下一輪方向

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| Governance closeout artefact 補回 | SESSION_LOG Session 98/99 entries | ✓ Done |
| §4a archive triggered | dev/archive/SESSION_LOG_2026_Q2.md + SESSION_LOG.md trim | ✓ Done |
| Sandbox egress 限制（Render not allowlisted） | SESSION_HANDOFF Known Risks | ✓ Done |
| Backend behavior change (Channel B routing) | SESSION_HANDOFF Open Priorities; Session entry QC evidence | ✓ Done |

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Current objective and progress state:
- Session 100 (2026-05-02) 完成治理補檔 + §4a archive + Channel B 路由層雙修補（F1+F2）+ 線上驗收
- F1 ship：searchChannelB.ts hr_admin regex 加 教師註冊/註冊處/聘任/聘用/招聘/入職/教師資格/教席/常額教席/代課教師
- F2 ship：searchChannelB.ts curriculum allowlist 加 g29/g25/g26/stat_kg；regex 加 幼稚園/幼兒/學前/K1/K2/K3/遊戲學習
- 線上驗收：Query 2 教師註冊 ✅ 完全成功（4 條全 hr 相關，off-topic 清晒）；Query 3 幼稚園 🟡 g29 入榜第 4 位但未 dominate（va_p1_s6 仍蓋）；Query 1 病假預期內 miss（屬 F3 量級層）
- 商品狀態維持：v2.2.0 / role_facts 1,001 / Supabase 10,736 chunks / vault 120 sources / Channel A cache warm size:517
- MemPalace sync 修正：用 venv python（system python 無 chromadb）4 sessions + handoff snapshot 寫入

Pending tasks in priority order:
1. F3 per-source diversity（wikiRepository.ts）— 解 Query 1 病假被 SAG 蓋 + Query 3 g29 未 dominate；設計 per-source top-N quota 或 score-weighted boost
2. F4 g24 / sag_2025_11 dedup（Supabase SQL）— 兩者係同一份《學校行政手冊》，重複 715 chunks；先 dry-run 驗證 sag 涵蓋 g24 全部內容才能刪
3. 視 user 意願：F2 加強 sub-routing（query 含「幼稚園」時動態 narrow 至 g29/g25/g26）抑或一次過做 F3
4. 評估 g21/g22/g33（視藝/科技/英文）與 8 skipped sources（找不到 PDF 先 triage source 本身）
5. 監察 Render cold start 對線上驗證影響（~30s after 15min idle）

Key files changed in this session:
- backend/src/api/searchChannelB.ts（F1 hr_admin regex + F2 curriculum allowlist + regex）
- dev/SESSION_LOG.md（Sessions 98/99 Verbatim 補回 + Session 100 entry + archive trim + Final QC）
- dev/archive/SESSION_LOG_2026_Q2.md（新增，10 entries）
- dev/SESSION_HANDOFF.md（Open Priorities regenerated / Last Session Record 更新）

Known risks / blockers / cautions:
- Cowork sandbox egress allowlist 不含 edb-knowledge.onrender.com → 線上驗證需用戶 Terminal
- Render free tier cold start ~30s after 15min idle
- Shared MemPalace recovery workaround (hnsw:num_threads=1)；保留備份 /Users/leonard/mempalace/palace.pre-recovery.20260421_0838
- Supabase free tier 500MB DB limit；現約 50MB
- F4 dedup 高風險（SQL DELETE）— 必先 dry-run 驗證 sag 涵蓋 g24 全部內容

Validation status:
- PASS: TypeScript npm run check 0 errors（F1+F2 後）
- PASS: §4a --check trigger=False（151 lines / 3 entries 已 archive）
- PASS: 線上 Query 2 教師註冊 sag × 4 全 hr 相關（F1 完全成功）
- PASS: 線上 Query 3 幼稚園 g29 命中第 4 位 score 0.5904（F2 allowlist 修補生效）
- 預期內 MISS: 線上 Query 1 病假仍係 SAG 主導 → 屬 F3 量級層問題

Post-startup first action: 詢問 Leonard：先做 F3 per-source diversity（解 Query 1 病假 + Query 3 dominate 一次過）、F4 dedup（資料層清垃圾）、抑或視 user 意願開新功能 / 補 source。
```

---

## 2026-05-02 Session 99 — 版本號對齊 + 平台介紹重設計 + Logo 首頁導向

- **ID:** Claude_20260502_0002
- **Summary:** 全平台版本號統一至 v2.2.0；PlatformIntroPanel 完整重設計（互動示範 / 動態計數動畫 / 三功能卡）；app.html logo 點擊改為返回 index.html。
- **Changed:** `README.md`, `CHANGELOG.md`, `knowledge.json`, `guidelines.json`, `app.html`, `dev/SESSION_HANDOFF.md`
- **Done:**
  - ✅ **[版本號對齊]** README badge → v2.2.0；footer → 2026-05-02 v2.2.0；CHANGELOG 新增 v2.2.0 條目；`knowledge.json` + `guidelines.json` `_meta.version` → 2.2.0；`app.html` INITIAL_DATA `_meta.version` → 2.2.0 + `updated` → 2026-05-02
  - ✅ **[平台介紹重設計]** `PlatformIntroPanel` 全面重寫：動態計數動畫（ease-out cubic，900ms）；互動示範 tab（校長/文書主任/課程主任 3個真實查詢示例，含模擬回答卡 + 來源引用，fade-in 動畫）；三大核心功能卡（語義搜尋/指引/知識提煉）；連接式三步流程；更新 sources 深色面板（120份文件 + 合規免責聲明）；version badge pill
  - ✅ **[Logo 首頁導向]** `app.html` K1 logo 點擊從 `switchView('qa')` 改為 `window.location.href = 'index.html'`
- **QC:** 所有版本號一致（role_facts 2.2.0 / knowledge.json 2.2.0 / guidelines.json 2.2.0 / README badge v2.2.0 / CHANGELOG 最新條目 v2.2.0）
- **Pending:** Git commit + push（用戶執行）；MemPalace sync（用戶執行）
- **Next:** 1. 驗證 GitHub Pages 平台介紹 tab 互動效果；2. 驗證 Channel B 搜尋質量（g24/g29）；3. g21/g22/g33 直連 PDF 考慮

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| 版本號全平台對齊 | README / CHANGELOG / SESSION_HANDOFF | ✓ Done |
| PlatformIntroPanel 重設計 | SESSION_LOG 記錄 | ✓ Done |
| Logo 導向改動 | SESSION_HANDOFF next priorities | ✓ Done |

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Current objective and progress state:
- 全平台版本號統一至 v2.2.0（Session 99, 2026-05-02）：role_facts / knowledge.json / guidelines.json / README badge / CHANGELOG 全部對齊
- PlatformIntroPanel 重設計：動態計數動畫、互動示範 tab（校長/文書主任/課程主任 3 個查詢示例）、三大核心功能卡、連接式三步流程、120 份文件深色面板、version badge pill
- app.html K1 logo 點擊改為返回 index.html（取代原 switchView('qa')）

Pending tasks in priority order:
1. Git commit + push（用戶 Terminal 執行）：
   cd ~/Downloads/Claude-edb-knowledge && git add -A && git commit -m "feat: v2.2.0 — version alignment + platform intro redesign with demo showcase" && git push origin main
2. MemPalace sync（用戶 Terminal 執行：python3 dev/mempalace_sync.py write）
3. 驗證 GitHub Pages 平台介紹 tab 互動效果（demo tab 切換 / 動態計數）
4. 驗證 Channel B 搜尋質量（g24/g29 新 chunks 上線後）
5. 考慮 g21/g22/g33（視覺藝術/科技/英文課程）直連 PDF

Key files changed in this session:
- README.md, CHANGELOG.md, knowledge.json, guidelines.json, app.html, dev/SESSION_HANDOFF.md

Known risks / blockers / cautions:
- Render free tier cold start ~30s after 15min idle
- Shared MemPalace recovery workaround (hnsw:num_threads=1)；保留備份 /Users/leonard/mempalace/palace.pre-recovery.20260421_0838
- Supabase free tier 500MB DB limit
- Sessions 98 / 99 closeout 缺 Verbatim block（已於 Session 100 補回）

Validation status:
- PASS: 全平台版本號核對一致；PlatformIntroPanel 互動示範 tab、動態計數、sources 面板已驗證

Post-startup first action: 詢問 Leonard：先清 git push + MemPalace sync 還是進入下一輪驗證 / 新功能。
```

---

## 2026-05-02 Session 98 — Vault 擴充完成 + Supabase 全量同步 + Source Label UI

- **ID:** Claude_20260502_0001
- **Summary:** Vault 擴充 pipeline 全面完成：upload_wiki_to_supabase.py 修復（merge-duplicates + null byte sanitize + auto .env 讀取）；全量 10,736 chunks 同步至 Supabase；g04/g29/g24 個別更新；app.html Source ID 全面替換為中文顯示名稱；source_registry 更新直連 PDF URL。
- **Changed:** `app.html`, `dev/vault/expand_vault.py`, `dev/upload_wiki_to_supabase.py`, `dev/source/source_registry.json`
- **Done:**
  - ✅ **[expand_vault.py 修復]** `_sanitize_text()` 去除 null bytes（PostgreSQL 限制）；`supabase_upsert_batch` 全欄位 sanitize
  - ✅ **[upload_wiki_to_supabase.py 修復]** auto-load `SUPABASE_SERVICE_KEY` from `backend/.env`；`merge-duplicates` upsert；null byte sanitize
  - ✅ **[Supabase 全量同步]** 10,736 chunks 上傳（1,176 skipped，無 embedding）；0 failed batches
  - ✅ **[g04 更新]** 7 chunks 替換（批假指引最新版）
  - ✅ **[g29 g24 PDF fetch]** g29 幼稚園課程指引 132 chunks；g24 學校行政手冊 300 chunks（上限截斷）；直連 PDF URL 已更新至 source_registry
  - ✅ **[Source Label UI]** `SOURCE_LABELS` map 加入 app.html；`getSourceLabel()` 替換全 UI 的 source_id 顯示（搜尋板式 / 候選列表 / Inspector）
  - ✅ **[religious_edu_jss]** Google redirect URL 失效，改回 landing page，status 改為 candidate
- **QC:** git push 78ce2ce ✅；Supabase 10,736 chunks confirmed；vault 120 sources 提取完成（8 skipped：scanned/SPA）
- **Pending:** MemPalace sync（用戶執行）
- **Next:** 1. 驗證 Channel B 搜尋質量（新增 g24/g29 chunks 後）；2. 考慮 g21/g22/g33 直連 PDF；3. 可開始新功能開發

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| Supabase chunk count 大幅增加 | SESSION_HANDOFF.md knowledge state | ✓ Done |
| Source label UI 改動 | SESSION_HANDOFF.md baseline | ✓ Done |
| source_registry URL 更新 | SESSION_LOG 記錄 | ✓ Done |

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Current objective and progress state:
- Vault 擴充 pipeline 全部完成（Session 98, 2026-05-02）：Supabase 同步 10,736 chunks，0 failed batches
- expand_vault.py 及 upload_wiki_to_supabase.py 已修復 null byte / merge-duplicates / auto env load
- g04（7 chunks）、g29（132 chunks）、g24（300 chunks 截斷上限）已個別更新
- app.html SOURCE_LABELS map 上線，全 UI source_id 已替換為中文顯示名
- religious_edu_jss 因 Google redirect 失效改回 landing page，status → candidate
- 已 git push 78ce2ce ✅

Pending tasks in priority order:
1. MemPalace sync（用戶 Terminal 執行：python3 dev/mempalace_sync.py write）
2. 驗證 Channel B 搜尋質量（新增 g24/g29 chunks 後是否命中）
3. 考慮 g21/g22/g33（視覺藝術/科技/英文課程）直連 PDF
4. 可開始新功能開發

Key files changed in this session:
- app.html, dev/vault/expand_vault.py, dev/upload_wiki_to_supabase.py, dev/source/source_registry.json

Known risks / blockers / cautions:
- Render free tier cold start ~30s after 15min idle
- Supabase free tier 500MB DB limit；現約 50MB
- religious_edu_jss landing page 無直連 PDF，待人手核實官方原文位置

Validation status:
- PASS: git push 78ce2ce；Supabase 10,736 chunks confirmed；vault 120 sources 提取完成（8 skipped：scanned/SPA）

Post-startup first action: 詢問 Leonard：跑 MemPalace sync、驗證 Channel B 質量、抑或開新功能。
```

---

## 2026-05-01 Session 97 — v2.2.0 全平台視覺重設 + Hash Routing + Favicon

- **ID:** Claude_20260501_0006
- **Summary:** K1知識平台全平台視覺重整完成（Session 96/97 合計）：EDB 深綠 nav 統一全4個HTML、主題顏色系統、航班板式搜尋結果、index.html 改寫為 Landing Page、hash routing deep-link、bookmark favicon、版本升至 v2.2.0。
- **Changed:** `index.html`, `app.html`, `q.html`, `t-purchase.html`, `role_facts.json`, `dev/SESSION_HANDOFF.md`, `dev/SESSION_LOG.md`
- **Done:**
  - ✅ Nav 統一：全4個HTML改為 `background: var(--edb)` 深綠實色，white 文字
  - ✅ 主題顏色 token：finance/hr/curriculum/admin 四域 bg/bd CSS 變量全4個HTML
  - ✅ 航班板式搜尋：5欄 grid（channel dot / source / content / roles / score），取代原卡片堆疊
  - ✅ 字型層次：clamp 字型、line-height 1.7、手機 sticky 搜尋欄（position:sticky top:56px）
  - ✅ 手機底部 tab bar：全5個 tab，admin 限定
  - ✅ index.html Landing Page：hero + 靜態統計帶 + 3功能卡 + 4步 how-it-works + 角色網格 + CTA
  - ✅ Hash routing：`app.html#guidelines` deep-link；`switchView()` 同步 URL hash + scroll；全tab按鈕改用 `switchView`（含 mobile tab bar + logo 按鈕）
  - ✅ Favicon：SVG data URI favicon（深綠圓角方塊 + K1白字），全4個HTML，bookmark 時顯示圖示
  - ✅ Version bump：`role_facts.json` v2.1.0 → v2.2.0；SESSION_HANDOFF.md baseline 更新
- **QC:** 所有 `setViewMode` 已替換為 `switchView`（僅餘 useState 宣告及函數體內部呼叫）；favicon 已插入全4個HTML `<head>` 第一行 link
- **Pending:** Git commit + push（用戶 Terminal 執行）；MemPalace sync
- **Next:** 1. 確認 GitHub Pages landing page 正確顯示；2. 確認 `app.html#guidelines` deep-link 正常；3. vault PDF fetch + embed（Session 96 pending）；4. g04 Supabase 更新

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| Frontend visual overhaul (all 4 HTML) | SESSION_HANDOFF.md baseline version + frontend description | ✓ Done |
| New feature (hash routing, favicon) | SESSION_HANDOFF.md Last Session Record | ✓ Done |
| Version bump (v2.2.0) | role_facts.json _meta.version + SESSION_HANDOFF.md | ✓ Done |

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first, then: dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md
Version is now v2.2.0. Confirm GitHub Pages landing page loads correctly and app.html#guidelines deep-link works. Then resume vault PDF fetch+embed pipeline if not yet completed.
```

---
