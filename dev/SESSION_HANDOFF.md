# Session Handoff

## Current Baseline
1. Version: **v1.3.1** (K1 EDB Knowledge Platform) — pushed to `main`; backend split-role compatibility bridge included
2. Core commands / features: K1 EDB Knowledge Dashboard (single HTML `k1-dashboard.html`, React 18 + Babel + Tailwind CDN). INITIAL_DATA 直接嵌入為 JS object literal（無 fetch，無 AppLoader）。107 facts, 7 topics, 全部 approved。4 view modes: 知識庫 / 指引文件庫 / 🔍 智能搜尋 / 📋 通告分析。Admin SHA-256 auth。雙匯出模式。同瀏覽器 localStorage 自動保存。Guidelines Library（39 EDB 文件）。**EDB Circular System 接口**：`knowledge.json` + `guidelines.json`（repo root）已生成並已 commit，供 EDB-AI-Circular-System 調用。
3. Regression baseline: **107 facts** across 7 topics, all approved. Dashboard UI role IDs remain `panel_chair` + `subject_head`, with display labels `主任` + `科主任`; `eo_admin` display label is `EO`. Dashboard embedded data and `data.json` use `科主任 / 主任 / EO` wording. Public `knowledge.json` v1.3.1 now uses split external role buckets `subject_head` + `panel_chair` + `all_roles` (no `department_head`). Local backup/export artifact `dev/knowledge/role_facts.json` still keeps the older merged `department_head` shape. All facts ≤ 80 chars, ≤5 per role key. 39 guideline documents. `guidelines.json`：39 EDB 文件 reference links（含 id/title/titleShort/url/year/format），按 topic 分組。
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
1. **[Phase 0 — 驗證]** Browser hard-refresh 4 public URLs，確認 GitHub Pages 反映 `v1.3.1`
2. **[Phase 1]** 建立 source registry + fact-source mapping：
   - 建立 `dev/source/source_registry.json`，seed SAG + Code of Aid + guidelines.json 中已有的 ~15 EDB 文件
   - 在 `role_facts.json` 各 topic block 加入 `_source_refs` 欄位（`_` prefix，不影響公開契約）
   - 完成後每條 fact 可追溯至少一個來源
3. **[品質]** Backend semantic quality regression：用 2–3 份真實 EDB 通告做 `POST /analyze-circular` 測試
4. **[Phase 2]** Source freshness monitoring script（Phase 1 穩定後）
5. **[EDB 側]** EDB agent 更新 `fetch_knowledge.py` 的 `department_head` stale path；初始化 EDB-Project-V3 git repo

## Known Risks / Blockers
1. EDB website pages sometimes 404 or restructured — guideline URLs may need updating
2. WebFetch tool cannot access www.edb.gov.hk (EGRESS_BLOCKED) — use browser MCP for new EDB research
3. Fact limit of 5 per role key may become constraining as knowledge base grows
4. IT topic source [1] (BYOD/interactive learning) still points to index page — no specific PDF found
5. Backend: `OPENAI_API_KEY` required at runtime; backend not deployed (local only)
6. **Backend uses ALL facts regardless of draft/approved status** — `knowledgeRepository.ts` loads raw `role_facts.json` without status filtering. Approval state lives only in the dashboard UI's in-memory `reviewState`. If only approved facts should be injected, export approved-only JSON and point backend to it.
7. **Admin password is client-side SHA-256 only** — not server-enforced; sufficient for single-user school admin scenario but not for multi-user adversarial contexts. Password: internal only.
8. **GitHub Pages deployment propagation / browser cache may lag after push** — if live page still shows older version text, verify again after hard refresh or incognito.
9. **Threshold raise to 0.45 is machine-verified but not live-smoke-verified yet** — precision should improve, but a real circular test is still needed.
10. **GitHub Pages deployment propagation may lag behind push by a short interval** — verify the live site after refresh if version text or button styling does not change immediately.
11. **GitHub Pages edits are only browser-persistent until a snapshot is written back** — localStorage keeps the same-browser state, but cross-device / long-term permanence still requires downloading a 管理快照 and committing it to the repo.
12. **Dashboard and external export wording are intentionally not identical** — dashboard uses split roles (`主任` / `科主任` / `EO`), while public `knowledge.json` is split-role external API data and local `dev/knowledge/role_facts.json` remains a merged backup/export artifact.
13. **knowledge.json schema 重大變更 v1.3.1** — `department_head` bucket 已移除，拆分為 `subject_head`（科主任）+ `panel_chair`（統籌主任）。EDB Circular System 須更新取值邏輯（見 Open Priorities #2）。
14. **K1_API_SPEC.md 已重寫並恢復公開** — 舊 spec 描述的 entry-list 格式從未實作；新 spec 記錄實際 role-bucketed 字串陣列格式，以及 subject_head vs panel_chair 定義。公開 URL：`https://leonard-wong-git.github.io/edb-knowledge/K1_API_SPEC.md`
15. **backend compatibility 已補上 bridge layer** — backend 現在同時接受舊 `department_head` 與新 `subject_head` / `panel_chair`；但本地 `dev/knowledge/role_facts.json` 仍是舊 merged schema。
16. **產品方向研究已暫停在 knowledge-base-first 結論** — 已確認 UI / product positioning 應以知識庫為核心，而非以「通告分析」作主舞台；但本 session 未進行任何 UI 結構變更，下一步仍應先集中在 circular 引用與回饋。
17. **Backend 預設知識源已切到 repo root `role_facts.json`** — `DEFAULT_KNOWLEDGE_PATH_SETTING` 已從 `../../../dev/knowledge/role_facts.json` 改為 `../../../role_facts.json`；機器驗證已確認 `subject_head` 與 `panel_chair` 在 `finance` topic 取回不同 facts，角色分辨恢復正常。（Session Codex_20260409_0001）
18. **AnalyzeCircularResponse 已補充診斷欄位** — response 現在包含 `similarity_scores` 與 `total_fact_chars`，方便後續 semantic regression 與 UI/consumer 調試。（Session Codex_20260409_0001）
19. **已同意 LLM-wiki phased approach（v2 plan）** — 用 LLM-wiki 概念統一理解：現有 facts/guidelines 已是 wiki，Phase 0 修 backend、Phase 1 加 source registry + `_source_refs` traceability、Phase 2 加 freshness monitoring、Phase 3 按需加 extraction/vault/compile。`SAG` + `Code of Aid` 為 spine sources。現階段 `knowledge.json` / `guidelines.json` / `role_facts.json` 接口不變。見 `dev/K1_KNOWLEDGE_OPERATING_SYSTEM_PLAN.md` v2。

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
10. Current failing checks: None

## Source Audit Summary (v1.0.0 baseline)
All 7 topics audited — Finance, HR, Activity, Student, Curriculum, IT, General. All source URLs updated to specific PDFs where available. See Session 13 log for details.

## Consolidation Watchlist
1. Rules currently duplicated across files: None
2. Areas showing accretive drift: None
3. Candidate items for consolidation / retirement: None

## Update Rule
This file and `dev/SESSION_LOG.md` must be updated at the end of every session.

## Last Session Record
1. UTC date: 2026-04-09
2. Session ID: Codex_20260409_0001
3. Completed:
   - ✅ 修正 backend 預設數據源：`DEFAULT_KNOWLEDGE_PATH_SETTING` 改為 repo root `role_facts.json`
   - ✅ 在 `AnalyzeCircularResponse` 加入 `similarity_scores` 與 `total_fact_chars`
   - ✅ `npm run check` / `npm run build` 通過
   - ✅ 驗證 `subject_head` 與 `panel_chair` 在 `finance` topic 返回 distinct facts
   - ✅ 同步更新 backend README 與 CODEBASE_CONTEXT
4. Pending: Browser live URL verification；Phase 1 source registry + `_source_refs`；Phase 2 freshness script；backend semantic regression；EDB 側 stale path
5. Next priorities (max 3): (1) Browser hard-refresh 4 public URLs (2) 建立 source_registry.json + seed entries (3) 用真實 EDB circular 做 backend semantic regression
6. Risks / blockers: Live URL 未 browser 確認；backend 仍未做真實 circular semantic regression；guidelines.json 仍未載入 backend；EDB-Project-V3 仍無 git
