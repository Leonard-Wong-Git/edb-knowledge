# Session Handoff

## Current Baseline
1. Version: **v1.3.1** (K1 EDB Knowledge Platform) — pushed to `main`; backend split-role compatibility bridge included
2. Core commands / features: K1 EDB Knowledge Dashboard (single HTML `k1-dashboard.html`, React 18 + Babel + Tailwind CDN). INITIAL_DATA 直接嵌入為 JS object literal（無 fetch，無 AppLoader）。107 facts, 7 topics, 全部 approved。4 view modes: 知識庫 / 指引文件庫 / 🔍 智能搜尋 / 📋 通告分析。Admin SHA-256 auth。雙匯出模式。同瀏覽器 localStorage 自動保存。Guidelines Library（39 EDB 文件）。**EDB Circular System 接口**：`knowledge.json` + `guidelines.json`（repo root）已生成並已 commit，供 EDB-AI-Circular-System 調用。
3. Regression baseline: **107 facts** across 7 topics, all approved. Dashboard UI role IDs remain `panel_chair` + `subject_head`, with display labels `主任` + `科主任`; `eo_admin` display label is `EO`. Dashboard embedded data and `data.json` use `科主任 / 主任 / EO` wording. Public `knowledge.json` v1.3.1 now uses split external role buckets `subject_head` + `panel_chair` + `all_roles` (no `department_head`). Repo-root `role_facts.json` is split-role `v2.0.0` and now includes backward-compatible `_source_refs` metadata on each topic block; local backup/export artifact `dev/knowledge/role_facts.json` still keeps the older merged `department_head` shape. All facts ≤ 80 chars, ≤5 per role key. 39 guideline documents. `guidelines.json`：39 EDB 文件 reference links（含 id/title/titleShort/url/year/format），按 topic 分組。`dev/source/source_registry.json` 現有 `149` 個 source entries，已擴充加入統計來源、課程索引 / 子文件條目、科學教育 / 科技教育 / PSHE / 藝術教育 / 體育 / 常識科 / 小學人文科 / 德育及公民教育課程文件，以及示例 circular source；其中 `pri_science` family 已補上 2025 指引 PDF 直連及頁面內主要通告 / 通函 / 教師專業發展條目。`dev/vault/` 目前有 `12` 個 catalogue/workspace，作為 pilot extracts / catalogues 使用，但未改動任何公開 JSON 接口。
4. Release / merge status: **v1.3.1 pushed to `main`**。`knowledge.json` 已由 `v1.3.0` bump 到 `v1.3.1`；backend package 已由 `0.1.0` bump 到 `0.1.1`，並加入 split-role compatibility bridge。Repo: `Leonard-Wong-Git/edb-knowledge`. Live URL: https://leonard-wong-git.github.io/edb-knowledge/k1-dashboard.html.
5. Active branch / environment: Single-file HTML (`k1-dashboard.html`, ~2275 lines). INITIAL_DATA 嵌入。TypeScript backend in `backend/`（本地 :8787，未部署，端對端 smoke test 已通過）。
6. External platforms / dependencies in scope: EDB website. CDN: React 18.2, Babel 7.23, Tailwind 2.2. Backend deps: openai@4.104.0, tsx, TypeScript. **EDB-AI-Circular-System**（獨立 repo，https://leonard-wong-git.github.io/EDB-AI-Circular-System/edb-dashboard.html）。

## Layer Map
1. Product / System Layer: Dashboard UI, fact data model, review workflow, JSON export, EDB data ingestion, Guidelines Library, Knowledge Platform backend.
2. Development Governance Layer: AGENTS.md session governance, handoff/log protocol.
3. Current task belongs to which layer: Product / System Layer (LLM-wiki phased architecture, source registry + traceability design) + Development Governance Layer (documentation sync).
4. Known layer-boundary risks: None currently.

## Mandatory Start Checklist
1. Read `dev/SESSION_HANDOFF.md`
2. Read `dev/SESSION_LOG.md`
3. Read `dev/CODEBASE_CONTEXT.md`
4. Read `dev/PROJECT_MASTER_SPEC.md` (if exists) — does not exist yet
5. Confirm working tree / file status
6. Run baseline checks: python3 validation of role_facts.json schema
7. Confirm environment: backend needs `OPENAI_API_KEY=sk-...` at runtime
8. Search for related SSOT / spec / runbook before change: `K1_KNOWLEDGE_INTERFACE_SPEC.md`

## Architecture Decision (Session 13 — 2026-03-23)
**Upgrade from keyword RAG → Semantic / Vector RAG (Consultative RAG)**
- `topicDetector.ts` uses OpenAI `text-embedding-3-small` + cosine similarity against 6 Chinese topic anchors
- Module-level anchor embedding cache; `SIMILARITY_THRESHOLD = 0.45`
- Dashboard 4th view mode "📋 通告分析" serves as the RAG test interface

## Open Priorities
1. **[品質]** Backend semantic quality regression：
   - 已有離線 regression harness：`cd backend && npm run regression:semantic`
   - schema consistency 的本地 spec drift 已修正
   - 下一步需用真實 `OPENAI_API_KEY` 補做 online regression，驗證 split-role facts、`similarity_scores`、`total_fact_chars`
2. **[Phase 1]** refine `dev/source/source_registry.json`：
   - 檢查新增 entries 的 `source_type` / `topic_tags` / notes / parent linkage 是否足夠精準
   - 為已入庫但未補齊的 child sources 回填 PDF / detail 直連 URL
   - 檢查 source count 擴張後是否需要把部分 family 提升為更清楚的父子層級
3. **[Phase 2]** Source freshness monitoring script（先做最小可行版本：比對 `last_checked_at` 與公開 URL 變動）
4. **[EDB 側]** EDB agent 更新 `fetch_knowledge.py` 的 `department_head` stale path；初始化 EDB-Project-V3 git repo

## Known Risks / Blockers
1. EDB website pages sometimes 404 or restructured — guideline URLs may need updating
2. WebFetch tool cannot access www.edb.gov.hk (EGRESS_BLOCKED) — use browser MCP for new EDB research
3. Fact limit of 5 per role key may become constraining as knowledge base grows
4. IT topic source [1] (BYOD/interactive learning) still points to index page — no specific PDF found
5. Backend: `OPENAI_API_KEY` required at runtime; backend not deployed (local only)
6. **Backend uses ALL facts regardless of draft/approved status** — `knowledgeRepository.ts` loads raw `role_facts.json` without status filtering. Approval state lives only in the dashboard UI's in-memory `reviewState`. If only approved facts should be injected, export approved-only JSON and point backend to it.
7. **Admin password is client-side SHA-256 only** — not server-enforced; sufficient for single-user school admin scenario but not for multi-user adversarial contexts. Password: internal only.
8. **GitHub Pages deployment propagation / browser cache may lag after push** — if future live page still shows older version text, verify again after hard refresh or incognito.
9. **Threshold raise to 0.45 is machine-verified but not live-smoke-verified yet** — precision should improve, but a real circular test is still needed.
10. **GitHub Pages deployment propagation may lag behind push by a short interval** — on future releases, verify the live site after refresh if version text or button styling does not change immediately.
11. **GitHub Pages edits are only browser-persistent until a snapshot is written back** — localStorage keeps the same-browser state, but cross-device / long-term permanence still requires downloading a 管理快照 and committing it to the repo.
12. **Dashboard and external export wording are intentionally not identical** — dashboard uses split roles (`主任` / `科主任` / `EO`), while public `knowledge.json` is split-role external API data and local `dev/knowledge/role_facts.json` remains a merged backup/export artifact.
13. **knowledge.json schema 重大變更 v1.3.1** — `department_head` bucket 已移除，拆分為 `subject_head`（科主任）+ `panel_chair`（統籌主任）。EDB Circular System 須更新取值邏輯（見 Open Priorities #2）。
14. **K1_API_SPEC.md 已重寫並恢復公開** — 舊 spec 描述的 entry-list 格式從未實作；新 spec 記錄實際 role-bucketed 字串陣列格式，以及 subject_head vs panel_chair 定義。公開 URL：`https://leonard-wong-git.github.io/edb-knowledge/K1_API_SPEC.md`
15. **backend compatibility 已補上 bridge layer** — backend 現在同時接受舊 `department_head` 與新 `subject_head` / `panel_chair`；但本地 `dev/knowledge/role_facts.json` 仍是舊 merged schema。
16. **產品方向研究已暫停在 knowledge-base-first 結論** — 已確認 UI / product positioning 應以知識庫為核心，而非以「通告分析」作主舞台；但本 session 未進行任何 UI 結構變更，下一步仍應先集中在 circular 引用與回饋。
17. **Backend 預設知識源已切到 repo root `role_facts.json`** — `DEFAULT_KNOWLEDGE_PATH_SETTING` 已從 `../../../dev/knowledge/role_facts.json` 改為 `../../../role_facts.json`；機器驗證已確認 `subject_head` 與 `panel_chair` 在 `finance` topic 取回不同 facts，角色分辨恢復正常。（Session Codex_20260409_0001）
18. **AnalyzeCircularResponse 已補充診斷欄位** — response 現在包含 `similarity_scores` 與 `total_fact_chars`，方便後續 semantic regression 與 UI/consumer 調試。（Session Codex_20260409_0001）
19. **已同意 LLM-wiki phased approach（v2 plan）** — 用 LLM-wiki 概念統一理解：現有 facts/guidelines 已是 wiki，Phase 0 修 backend、Phase 1 加 source registry + `_source_refs` traceability、Phase 2 加 freshness monitoring、Phase 3 按需加 extraction/vault/compile。`SAG` + `Code of Aid` 為 spine sources。現階段 `knowledge.json` / `guidelines.json` / `role_facts.json` 接口不變。見 `dev/K1_KNOWLEDGE_OPERATING_SYSTEM_PLAN.md` v2。
20. **LLM-wiki 的信任機制已明確化** — 方向不是做 autonomous LLM editor，而是以 source admission / freshness / fact proposal / approval / public compilation 五道 trust gates，逐步減少低風險的人手判斷；高風險變更仍保留人工批准。Phase 1 需把第一版 trust-gate policy 一起寫清楚。（Session Codex_20260410_0002）
21. **4 個公開 URL 已於 2026-04-10 live 驗證** — `k1-dashboard.html`、`knowledge.json`、`guidelines.json`、`K1_API_SPEC.md` 均可公開存取；其中 dashboard / knowledge / guidelines 已反映 `v1.3.1`。`K1_API_SPEC.md` 可公開讀取，但內容仍是較早的 live 版，待本地 docs commit push 後才會更新。（Session Codex_20260410_0002）
22. **Phase 1 source registry 已建立第一版** — `dev/source/source_registry.json` 已建立，現含 `41` 個 source entries（`2` spine sources + `39` guideline sources），並把第一版 lightweight trust-gate policy 放在同一 registry 檔案內。下一步重點轉為 `_source_refs` 與 registry refinement。（Session Codex_20260410_0004）
23. **`role_facts.json` 已加上 `_source_refs`** — repo-root `role_facts.json` 的 7 個 topic block 現已附帶來源追溯 `source_id` 陣列，使用 `_` prefix 作 backward-compatible metadata，不改動既有 facts / role keys。`K1_KNOWLEDGE_INTERFACE_SPEC.md` 亦已同步改為記錄 `_source_refs`，避免文件漂移。（Session Codex_20260410_0005）
24. **source registry / vault 已擴充試點** — `dev/source/source_registry.json` 現已加入統計來源、課程索引目錄頁、課程子文件條目與示例 circular source；`dev/vault/` 已有 catalogues、政策 circular extract 及統計 extracts。這些屬 LLM-wiki evidence workspace / search-to-source 試點，不影響現時 Circular System 對 `knowledge.json` / `guidelines.json` / `role_facts.json` 的讀取方式。（Session Claude_20260410_0006）
25. **已明確雙軌 fact model** — `statistical` facts 是可直接對 source extract 驗證的客觀數據，可走較輕審批；`policy` facts 仍是角色責任 / 程序要求 / 門檻判斷等詮釋性內容，必須保留人工批准。Circular System prompt injection 仍只應依賴已批准的 policy facts；vault/search path 則可指向原始來源 URL。（Session Claude_20260410_0006）
26. **科學教育課程文件已納入 registry / vault 結構** — `sci_curr_docs` 現已補上 2017 科學 KLA 指引、2025 小學科學指引、初中科學補充 / 課程框架，以及高中生物 / 化學 / 物理課程指引等 child sources；並建立 `dev/vault/science_edu_curr_docs/catalogue.json`。其中 `pri_science` family 現已進一步拆出 2023–2025 的主要通告 / 通函與教師專業發展文件，`pri_science_guide_2025` 亦已記錄官方 PDF 直連與本地副本 evidence。（Sessions Codex_20260410_0008 + Codex_20260410_0017）
27. **科技教育課程文件已納入 registry / vault 結構** — `tech_curr_docs` 現已補上 2017 科技教育 KLA 指引、小學計算思維－編程教育補充文件，以及高中 BAFS、健康管理與社會關懷、科技與生活、設計與應用科技、ICT 等課程文件 child sources；並建立 `dev/vault/technology_edu_curr_docs/catalogue.json`。其中 `ict_sss_2021` 現已補上 EdCity PDF 直連與本地副本 evidence；其餘個別 PDF 直連 URL 可日後再補。（Sessions Codex_20260410_0009 + Codex_20260410_0015）
28. **PSHE 課程文件已納入 registry / vault 結構** — `pshe_curr_docs` 現已補上中國歷史、公民經濟與社會、經濟、倫理與宗教、宗教教育、地理、歷史、旅遊與款待、生活與社會等 child sources，並建立 `dev/vault/pshe_curr_docs/catalogue.json`。目前仍以 user-paste catalogue 方式保存，個別 PDF / 詳情頁直連 URL 可日後再補。（Session Codex_20260410_0010）
29. **藝術教育課程文件已納入 registry / vault 結構** — `arts_curr_docs` 現已補上 2017 藝術教育 KLA 指引、音樂科課程指引 2024、高中音樂 2024 / 2015、國歌補充文件 2024、視覺藝術課程指引 2024 及高中視藝 2015；並建立 `dev/vault/arts_edu_curr_docs/catalogue.json`。其中藝術教育 KLA 2017、音樂科 2024、視藝科 2024、以及高中視藝 2015 已記錄 EDB PDF 直連和本地副本路徑，其餘 PDF 直連可日後再補。（Sessions Codex_20260410_0011 + Codex_20260410_0012)
30. **體育課程文件已納入 registry / vault 結構** — `pe_curr_docs` 現已補上體育 KLA 2017、高中體育 2023 / 2007-2015 等 core child sources，並建立 `dev/vault/pe_curr_docs/catalogue.json`。小學 / 中學建議學習範圍及六大學習範疇概覽目前先保留在 catalogue-only，不急於升級成正式 registry source。（Session Codex_20260410_0013）
31. **常識科（小學）課程文件已納入 registry / vault 結構** — `gs_pri_curr` 現已補上 2017 常識科課程指引 child source，並建立 `dev/vault/gs_primary_curr_docs/catalogue.json`。EDB PDF 直連與本地副本已記錄。常識科與小學人文科保留為兩個獨立 source family，只以 related linkage 連結。（Session Codex_20260410_0015）
32. **小學人文科課程文件已納入 registry / vault 結構** — `ph_pri_curr` 現已補上 2023/2024/2025 教育局通告 / 通函與 2025 課程指引 child sources，並建立 `dev/vault/ph_primary_curr_docs/catalogue.json`。其中 `EDBC_122025_C.pdf` 與 `Primary_Humanities_Curriculum_Guide.pdf` 已記錄 EDB PDF 直連與本地副本；活動入口暫保留為 catalogue-only。（Session Codex_20260410_0015）
33. **Level 1 LLM-wiki pipeline 首次端對端試點完成** — 以 `EDBC_122025_C.pdf`（EDBC 12/2025）為試點：PDF 上傳 → pdfplumber 提取 → vault 儲存 → AI 對照現有 facts → 提出候選 → 人工批准 → 寫入 role_facts.json + knowledge.json + _source_refs。C2/C3/C4 已批准寫入 `curriculum` topic；C1 由用戶決定不加入（all_roles 已達 5 facts 上限）。Source registry 現共 136 entries。（Session Claude_20260410_0016）
34. **德育及公民教育課程文件已納入 registry / vault 結構** — `moral_civic_curr` 現已拆出《價值觀教育課程架構（試行版）》（2021）、教育局通函第183/2023號、《中學教育課程指引》(2017) 分冊6A、《小學教育課程指引》(2024) 及《德育及公民教育課程架構》(2008) 五個 child entries，並建立 `dev/vault/moral_civic_curr/catalogue.json`。個別 PDF 直連仍可日後再補。（Session Codex_20260410_0018）
35. **本 session 已整理知識庫清單視圖** — 已按現況盤點 7 個主知識 topic、主要 curriculum / policy family 與 vault catalogues，方便之後把 repo 內現有知識、文件篇與 source family 整理成更正式的 operator-facing inventory。（Session Codex_20260410_0019）
36. **backend semantic regression harness 已建立** — `backend/scripts/semanticRegression.ts` 與 `npm run regression:semantic` 已加入。現可離線檢查 topic regression、role-bucket regression、schema consistency regression 及 real circular retrieval regression；離線結果已確認 `EDBC 12/2025` 與 `EDBC 17/2024` retrieval 命中 `curriculum`。本地 `K1_API_SPEC.md` 版本漂移已於 2026-04-11 修正；full online regression 仍受 `OPENAI_API_KEY` 缺失阻塞。（Sessions Codex_20260410_0020 + Codex_20260411_0001）

## Regression / Verification Notes
1. Required checks: All facts ≤ 80 chars, ≤ 5 per role key, valid topic/role IDs, JSON schema compliance
2. Backend build checks: `npm run check` (tsc --noEmit) exits 0 ✅ (verified Session 16)
3. Backend runtime: `npm run dev` starts server on :8787 ✅ (verified Session 15)
4. All 81 facts ≤ 80 chars ✅ (verified Sessions 16 + 19)
5. role_facts.json synced to INITIAL_DATA ✅ (Session 19 — procurement thresholds updated, 3-year record retention)
6. Admin mode: SHA-256 hash verified by Python + confirmed in 10-point grep check ✅ (Session 19)
7. Backend default knowledge path now resolves to repo-root `role_facts.json` ✅ (`node --input-type=module ...`; Session Codex_20260409_0001)
8. `subject_head` vs `panel_chair` split-role selection verified on `finance` topic ✅ (Session Codex_20260409_0001)
9. `AnalyzeCircularResponse` now returns `similarity_scores` + `total_fact_chars` in compiled backend output ✅ (`npm run build` + `node --input-type=module ...`; Session Codex_20260409_0001)
10. Repo-root `role_facts.json` now has `_source_refs` on all 7 topic blocks, with role keys preserved ✅ (`python3` JSON validation; Session Codex_20260410_0005)
11. Current failing checks:
   - offline topic regression 仍有多個固定 query 落到 `general`
   - full online semantic regression 仍待 `OPENAI_API_KEY`

## Source Audit Summary (v1.0.0 baseline)
All 7 topics audited — Finance, HR, Activity, Student, Curriculum, IT, General. All source URLs updated to specific PDFs where available. See Session 13 log for details.

## Consolidation Watchlist
1. Rules currently duplicated across files: None
2. Areas showing accretive drift: None
3. Candidate items for consolidation / retirement: None

## Update Rule
This file and `dev/SESSION_LOG.md` must be updated at the end of every session.

## Last Session Record
1. UTC date: 2026-04-10
2. Session ID: Codex_20260411_0001
3. Completed:
   - ✅ 修正 `K1_API_SPEC.md` 本地版本 / 日期漂移
   - ✅ 令本地 schema consistency regression 與 `knowledge.json` / `guidelines.json` 對齊至 `v1.3.1`
   - ⚠️ `K1_API_SPEC.md` live page 仍待後續 push 才會更新
   - ⚠️ online regression 仍受 `OPENAI_API_KEY` 缺失阻塞
4. Pending: online backend semantic regression；registry refinement；Phase 2 freshness script；EDB 側 stale path；docs commit 尚未 push；多個 family 的個別 PDF / detail 直連 URL 仍待補完
5. Next priorities (max 3): (1) 用真實 `OPENAI_API_KEY` 補做 online backend semantic regression (2) 回填已入庫來源的 direct PDF / detail URL (3) 定義最小可行 freshness flow
6. Risks / blockers: guidelines.json 仍未載入 backend；online regression 仍受 `OPENAI_API_KEY` 缺失阻塞；`K1_API_SPEC.md` live page 仍待 push 才會追上本地；EDB-Project-V3 仍無 git；source registry 已增至 149 entries，需留意維護成本；多個 family 仍有 PDF / DOCX / detail 直連待補完
