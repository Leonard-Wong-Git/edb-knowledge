# Session Handoff

## Current Baseline
1. Version: **v1.2.2** (K1 EDB Knowledge Platform) — Live on GitHub Pages ✅
2. Core commands / features: K1 EDB Knowledge Dashboard (single HTML `k1-dashboard.html`, React 18 + Babel + Tailwind CDN). INITIAL_DATA 直接嵌入為 JS object literal（無 fetch，無 AppLoader）。107 facts, 7 topics, 全部 approved。4 view modes: 知識庫 / 指引文件庫 / 🔍 智能搜尋 / 📋 通告分析。Admin SHA-256 auth。雙匯出模式。同瀏覽器 localStorage 自動保存。Guidelines Library（39 EDB 文件）。**EDB Circular System 接口**：`knowledge.json` + `guidelines.json`（repo root）已生成並已 commit，供 EDB-AI-Circular-System 調用。
3. Regression baseline: **107 facts** across 7 topics, all approved. Dashboard UI role IDs remain `panel_chair` + `subject_head`, with display labels now `主任` + `科主任`; `eo_admin` display label is `EO`. Dashboard embedded data and `data.json` use `科主任 / 主任 / EO` wording. External `knowledge.json` / `role_facts.json` keep the merged `department_head` contract and currently use通用 `主任 / EO` wording for the combined role. All facts ≤ 80 chars, ≤5 per role key. 39 guideline documents. `guidelines.json`：39 EDB 文件 reference links（含 id/title/titleShort/url/year/format），按 topic 分組。
4. Release / merge status: **v1.2.2，已 push 至 GitHub**。最新角色命名調整 commits `cd96a22`（主任 / EO wording）與 `2bea03e`（dashboard role split refinement）已推送到 `main`。Repo: `Leonard-Wong-Git/edb-knowledge`. Live URL: https://leonard-wong-git.github.io/edb-knowledge/k1-dashboard.html.
5. Active branch / environment: Single-file HTML (`k1-dashboard.html`, ~2275 lines). INITIAL_DATA 嵌入。TypeScript backend in `backend/`（本地 :8787，未部署，端對端 smoke test 已通過）。
6. External platforms / dependencies in scope: EDB website. CDN: React 18.2, Babel 7.23, Tailwind 2.2. Backend deps: openai@4.104.0, tsx, TypeScript. **EDB-AI-Circular-System**（獨立 repo，https://leonard-wong-git.github.io/EDB-AI-Circular-System/edb-dashboard.html）。

## Layer Map
1. Product / System Layer: Dashboard UI, fact data model, review workflow, JSON export, EDB data ingestion, Guidelines Library, Knowledge Platform backend.
2. Development Governance Layer: AGENTS.md session governance, handoff/log protocol.
3. Current task belongs to which layer: Product / System Layer (dashboard role naming consistency).
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
1. **[EDB 側更新]** 通知 EDB Circular System agent 更新 knowledge.json 取值邏輯：
   - 舊：`knowledge[topic].get("department_head", []) + knowledge[topic].get("all_roles", [])`
   - 新：`knowledge[topic].get("subject_head", []) + knowledge[topic].get("panel_chair", []) + knowledge[topic].get("all_roles", [])`
2. **[品質]** Backend semantic quality regression：用 2–3 份真實 EDB 通告做 `POST /analyze-circular` 測試，驗證 topic detection 與 `used_facts` 合理性
3. **[K1 後端同步]** `knowledgeRepository.ts` 目前讀取 `role_facts.json`（dashboard 格式，panel_chair/subject_head）；確認後端 knowledgeSelector.ts 能正確處理新 schema

## Known Risks / Blockers
1. EDB website pages sometimes 404 or restructured — guideline URLs may need updating
2. WebFetch tool cannot access www.edb.gov.hk (EGRESS_BLOCKED) — use browser MCP for new EDB research
3. Fact limit of 5 per role key may become constraining as knowledge base grows
4. IT topic source [1] (BYOD/interactive learning) still points to index page — no specific PDF found
5. Backend: `OPENAI_API_KEY` required at runtime; backend not deployed (local only)
6. **Backend uses ALL facts regardless of draft/approved status** — `knowledgeRepository.ts` loads raw `role_facts.json` without status filtering. Approval state lives only in the dashboard UI's in-memory `reviewState`. If only approved facts should be injected, export approved-only JSON and point backend to it.
7. **Admin password is client-side SHA-256 only** — not server-enforced; sufficient for single-user school admin scenario but not for multi-user adversarial contexts. Password: internal only.
8. **VM push remains blocked for future releases** — direct `git push origin main` from this VM still returns HTTP 403 proxy; any future pushes must be run from the user's local terminal.
9. **Threshold raise to 0.45 is machine-verified but not live-smoke-verified yet** — precision should improve, but a real circular test is still needed.
10. **GitHub Pages deployment propagation may lag behind push by a short interval** — verify the live site after refresh if version text or button styling does not change immediately.
11. **GitHub Pages edits are only browser-persistent until a snapshot is written back** — localStorage keeps the same-browser state, but cross-device / long-term permanence still requires downloading a 管理快照 and committing it to the repo.
12. **Dashboard and external export wording are intentionally not identical** — dashboard uses split roles (`主任` / `科主任` / `EO`), while exported `department_head` remains a merged external role with generic wording pending explicit decision.
13. **knowledge.json schema 重大變更 v1.3.0** — `department_head` bucket 已移除，拆分為 `subject_head`（科主任）+ `panel_chair`（統籌主任）。EDB Circular System 須更新取值邏輯（見 Open Priorities #1）。
14. **K1_API_SPEC.md 已重寫並恢復公開** — 舊 spec 描述的 entry-list 格式從未實作；新 spec 記錄實際 role-bucketed 字串陣列格式，以及 subject_head vs panel_chair 定義。公開 URL：`https://leonard-wong-git.github.io/edb-knowledge/K1_API_SPEC.md`

## Regression / Verification Notes
1. Required checks: All facts ≤ 80 chars, ≤ 5 per role key, valid topic/role IDs, JSON schema compliance
2. Backend build checks: `npm run check` (tsc --noEmit) exits 0 ✅ (verified Session 16)
3. Backend runtime: `npm run dev` starts server on :8787 ✅ (verified Session 15)
4. All 81 facts ≤ 80 chars ✅ (verified Sessions 16 + 19)
5. role_facts.json synced to INITIAL_DATA ✅ (Session 19 — procurement thresholds updated, 3-year record retention)
6. Admin mode: SHA-256 hash verified by Python + confirmed in 10-point grep check ✅ (Session 19)
7. Current failing checks: None

## Source Audit Summary (v1.0.0 baseline)
All 7 topics audited — Finance, HR, Activity, Student, Curriculum, IT, General. All source URLs updated to specific PDFs where available. See Session 13 log for details.

## Consolidation Watchlist
1. Rules currently duplicated across files: None
2. Areas showing accretive drift: None
3. Candidate items for consolidation / retirement: None

## Update Rule
This file and `dev/SESSION_LOG.md` must be updated at the end of every session.

## Last Session Record
1. UTC date: 2026-04-08
2. Session ID: Claude_20260408_0002
3. Completed:
   - ✅ 回應 EDB Circular System agent 的 4 個整合問題
   - ✅ 確認 knowledge.json stable schema：topic → role-bucket → string arrays
   - ✅ 確認 `department_head` 拆分決策：→ `subject_head`（科主任）+ `panel_chair`（統籌主任）
   - ✅ 重寫 knowledge.json v1.3.0：移除 `department_head`，加入 `subject_head` + `panel_chair`（8 事實用 dashboard 原文，panel_chair 保留 [角色] 標注）
   - ✅ 重寫 K1_API_SPEC.md：正確記錄實際 schema；加入 subject_head vs panel_chair 定義；版本歷史
   - ✅ K1_API_SPEC.md 恢復 repo root（公開 URL 恢復）；dev/K1_API_SPEC.md 已刪除
   - ✅ 用戶從 Mac terminal push 成功
4. Pending: EDB 側更新取值邏輯；backend knowledgeSelector.ts 確認兼容新 schema；backend regression test
5. Next priorities (max 3): (1) 通知 EDB 側更新 subject_head+panel_chair 取值邏輯 (2) backend knowledgeSelector.ts schema 兼容確認 (3) backend semantic quality regression
6. Risks / blockers: EDB Circular System 仍使用舊 department_head 取值直至更新；knowledgeRepository.ts 讀 role_facts.json（已有 panel_chair/subject_head），但 knowledgeSelector.ts 的角色篩選邏輯未驗證新 key
