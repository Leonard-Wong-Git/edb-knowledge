# Session Log

<!-- Archives: dev/archive/ — entries moved when >400 lines or oldest entry >30 days -->

## 2026-05-03 Session 105 — 健康檢查 + 三項 backlog audit（無動 code，純 planning）

- **ID:** Claude_20260503_0002
- **Summary:** 應 user 連續做 E→B→D→A 嘅請求，完成全 sandbox 內 audit：(E) 健康檢查無 drift；(B) g21/g22/g33 三個 source_type=pdf 但 url_primary 全缺，需要 user 開 EDB 補；(D) Query expansion 弱點分析，curriculum 同 activity vocabulary 最淺，候選驗證 query 已列；(A) vault refresh 兩分項 — 學校行政手冊統一 source_id 策略 1（軟 dedup 已 ship）足夠，策略 2（徹底 refetch）留下輪；13 problematic entries 三類處理方案出齊（6 已 fallback / 2 需 EDB 找 / 5 等 user 上傳 xlsx）。本 session 不動 backend code，純 audit + action plan。
- **Changed:** `dev/SESSION_LOG.md`, `dev/SESSION_HANDOFF.md`
- **Done:**
  - ✅ **[E 健康檢查]** 三層 facts v2.3.0 / 792 一致；governance 5 文件齊全（41-21KB）；12 backup 快照；2 archive quarterly 文件（Q1 84KB / Q2 421KB）
  - ✅ **[B g21/g22/g33 triage]** 三者 source_type='pdf' 但 url_primary 全缺，現只有 landing page；需要 user 開 EDB 對應 KLA 安全指引 / 課程文件總頁 inspect 直連
  - ✅ **[D Query expansion 候選]** vocabulary 字數 finance:5 / hr_admin:11 / activity:2 / curriculum:3；觸發詞數 finance:27 / hr_admin:32 / activity:4 / curriculum:31；候選驗證 query 包：finance「校董會經費批核程序」/ curriculum「資優學生識別準則 / 校本評核 SBA 安排 / STEM 跨學科專題」/ activity「全方位學習津貼開支類別 / 課外活動安排上限」
  - ✅ **[A vault refresh 計劃]** 學校行政手冊統一 = 策略 1（已 ship 軟 dedup）足夠；13 entries 分三類：6 URL 失效已 fallback（無 immediate action）/ 2 直連未補（sci_kla_guide_2017 + pri_science_cert_application_form，需 user EDB inspect）/ 5 xlsx 待上傳（5 個 stat_ 系列）
- **QC:** Sandbox audit 全部 read-only，無破壞；無新 governance 違規；§4a check trigger 視乎 entry 大小決定
- **Pending（用戶 Terminal / browser action）:**
  - Git commit + push（Session 105 entry + handoff 更新）
  - 視 user 揀方向：跑 Query expansion 驗證 query（最快出實證）/ 開 EDB 找 g21-22-33 PDF / 下載 xlsx 上 vault / 開新功能（C 留尾段）
- **Next:** 1. 由 user 揀新方向；2. 任何 backlog 項目都已有清晰 action plan，可隨時取一條 ship

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| Audit / planning only (no code change) | SESSION_LOG entry + SESSION_HANDOFF Open Priorities updated context | ✓ Done |

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Current objective and progress state:
- Session 105 (2026-05-03) 完成全 sandbox audit：健康檢查無 drift / g21-22-33 PDF 直連缺 / Query expansion 候選分析 / vault refresh 計劃，無動 code
- 商品狀態：v2.3.0 / role_facts 792 / Supabase 10,736 chunks / vault 120 sources

Pending tasks in priority order:
1. 揀新方向（Query expansion 驗證 query 線上跑 / 開 EDB 找 g21-22-33 PDF / xlsx 下載 / 新功能 / 其他）
2. 學校行政手冊徹底 refetch 統一 source_id（backlog；軟 dedup 已 ship 工作正常，唔急）
3. 6 個 URL 失效 entries 下輪 vault refresh 順手核
4. 開新功能方向（admin 端 Channel B prompt editor / 新區塊 / Circular System 整合）
5. Channel A embedding cache 監察

Key files changed in this session:
- dev/SESSION_LOG.md（Session 105 audit entry）
- dev/SESSION_HANDOFF.md（Open Priorities regenerated 反映 audit 結果）

Known risks / blockers / cautions:
- Cowork sandbox egress allowlist 不含 edb.gov.hk → URL inspect 同 xlsx 下載需 user browser
- Cowork sandbox egress allowlist 不含 edb-knowledge.onrender.com → 線上 query 驗證需用戶 Terminal
- Render free tier cold start ~30s after 15min idle
- Mac Python.framework 缺 SSL CA bundle，Supabase REST 直接 hit 會 SSLCertVerificationError；要用 curl 繞
- Shared MemPalace recovery workaround (hnsw:num_threads=1)；保留備份 /Users/leonard/mempalace/palace.pre-recovery.20260421_0838
- Supabase free tier 500MB DB limit；現約 50MB

Validation status:
- PASS: 三層 facts v2.3.0/792 一致；governance 文件齊全；無 git uncommitted（除本 session edit）
- PASS: 全部 audit 結果 sandbox 內驗證

Post-startup first action: 詢問 Leonard 揀方向（Query expansion 線上驗證 query / EDB PDF 補完 / xlsx 上傳 / 新功能 / 其他）。
```

---

## 2026-05-03 Session 104 — Query Expansion 補病假 vocabulary（chunk semantic 層救濟）

- **ID:** Claude_20260503_0001
- **Summary:** Session 103 線上驗收顯示來源別名 + 配額 ship 後 sag 維持 cap=3 + g24 完全唔出（兩層 ranking 修補實證生效），但 g04 病假指引仍未入榜 — 鎖定根因屬 chunk-level embedding semantic 問題（g04 chunks「首年 28 日 / 上限 168 日」對 query「教師病假上限多少天」cosine 真係低於 0.08 threshold）。本 session 試 Query expansion 路徑：擴充 hr_admin expansion vocabulary，加入「病假 首年 168 日 上限 醫生證明 教師註冊 聘任」7 個 specific keyword，目標 boost g04 chunks 嘅 query embedding cosine。
- **Changed:** `backend/src/api/searchChannelB.ts`（QUERY_EXPANSIONS.hr_admin 擴充）
- **Done:**
  - ✅ **[Query expansion 擴充]** hr_admin vocabulary 由「教職員假期 批假 薪酬 操守」改為「教職員假期 批假 薪酬 操守 病假 首年 168日 上限 醫生證明 教師註冊 聘任」
  - ✅ **[擴充原則]** 加少數最 specific 嘅子議題 keyword（病假 / 註冊聘任），唔過度膨脹避免稀釋 query embedding focus
- **QC:** TypeScript `npm run check` PASS 0 errors；commit 6c8a663 已 push
- **線上驗收（用戶 Terminal curl 完成）:** ✅ g04 第 1 位 score **0.7247**（之前 < 0.08 完全唔出）；synthesis 100% 準確引用 g04 內容「首年 28 日 / 其後 48 日 / 上限 168 日 / 120 日門檻按月更新」；之前混淆 SAG 學校假期表「366 日」嘅錯誤答案徹底消除；sag chunks cap=3 仍生效
- **Pending（用戶 Terminal 執行）:**
  - Final git push 含本次 closeout 後續 edit
- **Next:** 1. Channel B 病假 query root cause 已根治，下節由 user 揀新方向；2. 4 輪治理完整 case study 已記錄，可作其他 query / topic 改善模板

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| Backend behavior change (Channel B query expansion) | SESSION_HANDOFF Open Priorities; Session entry QC evidence | ✓ Done |

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Current objective and progress state:
- Session 104 (2026-05-03) ship Query expansion 擴充 hr_admin vocabulary 加病假 / 教師註冊 specific keyword，目標令 g04 / g05 / g11 chunks 嘅 query embedding cosine 升過 0.08 threshold
- 累積三輪 Channel B ranking 治理（Session 100 routing + 101 quota + 103 alias）已實證全部生效；剩低 chunk-level embedding semantic 屬 Session 104 expansion 嘅救濟對象
- 商品狀態：v2.3.0 / role_facts 792 / Supabase 10,736 chunks / vault 120 sources

Pending tasks in priority order:
1. 線上重 curl 教師病假 query 驗證 expansion 效果（用戶 Terminal）
2. 如果 expansion 仍唔夠：考慮 re-chunk g04 加 title prefix（chunk content 層救濟，工程量大）
3. vault refresh backlog（學校行政手冊統一 source_id + 13 problematic entries）
4. 評估視藝/科技/英文課程指引（g21/g22/g33）直連 PDF 必要性
5. 開新功能方向（admin 端 Channel B prompt editor / 新區塊 / 其他）

Key files changed in this session:
- backend/src/api/searchChannelB.ts（QUERY_EXPANSIONS.hr_admin 擴充病假 / 教師註冊 vocabulary）
- dev/SESSION_LOG.md（Session 104 entry）
- dev/SESSION_HANDOFF.md（Last Session Record / Open Priorities 更新）

Known risks / blockers / cautions:
- Cowork sandbox egress allowlist 不含 edb-knowledge.onrender.com → 線上驗證需用戶 Terminal
- Render free tier cold start ~30s after 15min idle
- Mac Python.framework 缺 SSL CA bundle，Supabase REST 直接 hit 會 SSLCertVerificationError；要用 curl 繞
- Shared MemPalace recovery workaround (hnsw:num_threads=1)；保留備份 /Users/leonard/mempalace/palace.pre-recovery.20260421_0838
- Supabase free tier 500MB DB limit；現約 50MB
- Query expansion 加太多 vocabulary 會稀釋 query embedding focus；今次只加 7 個最 specific keyword

Validation status:
- PASS: TypeScript npm run check 0 errors
- PASS: 線上端對端驗收 — g04 第 1 位 score 0.7247；synthesis 100% 準確引用 g04 真實批假指引內容；4 輪 ranking + semantic 治理全部生效

Post-startup first action: 詢問 Leonard：Channel B 病假 query 根因已治，下節揀新方向（vault refresh / 新功能 / 其他 query 質量改善）。
```

---

## 2026-05-02 Session 103 — 學校行政手冊來源別名 + Source Triage

- **ID:** Claude_20260502_0006
- **Summary:** wikiRepository 加 SOURCE_ALIASES map（g24 → sag_2025_11），quota gate 用 canonical source 計數，解 Session 102 dry-run 揭發嘅雙重 ingestion 重複佔配額問題。同步完成 source_registry triage：13 entries 有問題（6 URL 失效已 fallback / 2 直連未補 / 5 待 user 上傳 xlsx），全部唔屬「需要設計 fallback pipeline」嘅候選，按 memory 規範保留現狀。
- **Changed:** `backend/src/lib/wikiRepository.ts`
- **Done:**
  - ✅ **[來源別名映射]** wikiRepository.ts 加 `SOURCE_ALIASES = { g24: 'sag_2025_11' }` + `canonicalSource()` helper；JSDoc 詳述背景（Session 76 partial vs Session 98 whole-doc 兩種切割）
  - ✅ **[Quota gate 改用 canonical]** per-source quota 計數時 g24 + sag_2025_11 共享同一 bucket，避免兩個 source_id 同時佔 cap
  - ✅ **[本地 sanity test PASS]** mock chunks: sag×3 + g24×2 + va×2 + g04×1 + topK=5 cap=2 → 結果 sag-1 + g24-1（共佔 cap=2）+ va×2 + g04×1，g04 終於入榜（之前被學校行政手冊雙倍佔位蓋過）
  - ✅ **[Source registry triage]** 掃 151 sources：149 verified / 1 superseded / 1 candidate；按 source_type 同 notes 分類有問題嘅 13 entries（6 URL 失效 / 2 直連未補 / 5 待 user 上傳）
  - ✅ **[Triage 結論]** 全部 13 entries 唔屬「需要硬塞 fallback pipeline」候選；URL 失效嘅已有 landing page workaround，xlsx 等 user action，留 backlog 下輪 vault refresh 順手核
- **QC:** TypeScript `npm run check` PASS 0 errors；本地 alias quota sanity test PASS
- **Pending（用戶 Terminal 執行）:**
  - Git commit + push（含 wikiRepository alias + Session 103 entry）
  - 線上重 curl 教師病假 query 驗證 g04 是否真係入榜（理論上應該有，因為 sag/g24 共享 cap=3 釋出位）
- **Next:** 1. 收線上驗證結果；2. 視乎 user 開新方向；3. vault refresh backlog（學校行政手冊統一 source_id + 13 problematic entries 順手核）

### DOC_SYNC Matrix Scan
| Change Category | Required Doc Updates | Status |
|---|---|---|
| Backend behavior change (Channel B quota canonical) | SESSION_HANDOFF Open Priorities; Session entry QC evidence | ✓ Done |
| Source registry triage 報告 | Session 103 entry triage 章節 | ✓ Done |

### Next Session Handoff Prompt (Verbatim)
```text
Read AGENTS.md first (governance SSOT), then follow its §1 startup sequence:
dev/SESSION_HANDOFF.md → dev/SESSION_LOG.md → dev/CODEBASE_CONTEXT.md (if exists) → dev/PROJECT_MASTER_SPEC.md (if exists)

Current objective and progress state:
- Session 103 (2026-05-02) ship 學校行政手冊來源別名映射：wikiRepository.ts SOURCE_ALIASES map { g24 → sag_2025_11 }；quota gate 用 canonicalSource() 計數，兩個 source_id 共享一個 cap bucket
- 本地 sanity test 證明：g24/sag 共享 cap=2 之後釋出位俾 g04（教師病假 query 預期改善）
- Source registry triage：151 sources 入面 13 entries 有問題，全屬 source 本身狀態（URL 失效 / 待 user 上傳），唔需要 fallback pipeline
- 商品狀態：v2.3.0 / role_facts 792 / Supabase 10,736 chunks / vault 120 sources

Pending tasks in priority order:
1. 線上重 curl 教師病假 query 驗證 g04 是否入榜（用戶 Terminal）
2. vault refresh backlog（學校行政手冊統一 source_id + 13 problematic entries 順手核）
3. 評估視藝/科技/英文課程指引（g21/g22/g33）直連 PDF 必要性
4. 開新功能方向（admin 端 Channel B prompt editor / 新區塊 / 其他）
5. 監察 Render cold start 對線上驗證影響

Key files changed in this session:
- backend/src/lib/wikiRepository.ts（SOURCE_ALIASES map + canonicalSource() helper + quota gate 改用 canonical）
- dev/SESSION_LOG.md（Session 103 entry）
- dev/SESSION_HANDOFF.md（Open Priorities regenerated）

Known risks / blockers / cautions:
- Cowork sandbox egress allowlist 不含 edb-knowledge.onrender.com → 線上驗證需用戶 Terminal
- Render free tier cold start ~30s after 15min idle
- Mac Python.framework 缺 SSL CA bundle，Supabase REST 直接 hit 會 SSLCertVerificationError；要用 curl 繞
- Shared MemPalace recovery workaround (hnsw:num_threads=1)；保留備份 /Users/leonard/mempalace/palace.pre-recovery.20260421_0838
- Supabase free tier 500MB DB limit；現約 50MB

Validation status:
- PASS: TypeScript npm run check 0 errors
- PASS: 本地 alias quota sanity test（g24+sag 共享 cap，g04 入榜）
- PASS: Source registry triage（13 entries 分類完成，無需 fallback）

Post-startup first action: 詢問 Leonard：線上 curl 結果 / 開新功能 / vault refresh backlog。
```

---

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
