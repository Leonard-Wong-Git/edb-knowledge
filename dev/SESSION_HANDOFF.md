# Session Handoff

## Current Baseline
1. Version: **v1.2.2** (K1 EDB Knowledge Platform) — Live on GitHub Pages ✅
2. Core commands / features: K1 EDB Knowledge Dashboard (single HTML `k1-dashboard.html`, React 18 + Babel + Tailwind CDN). INITIAL_DATA 直接嵌入為 JS object literal（無 fetch，無 AppLoader）。107 facts, 7 topics, 全部 approved。4 view modes: 知識庫 / 指引文件庫 / 🔍 智能搜尋 / 📋 通告分析。Admin SHA-256 auth。雙匯出模式。同瀏覽器 localStorage 自動保存。Guidelines Library（39 EDB 文件）。**EDB Circular System 接口**：`knowledge.json`（repo root）已生成，供 EDB-AI-Circular-System 調用。
3. Regression baseline: **107 facts** across 7 topics, all approved. `panel_chair` + `subject_head` in dashboard UI. `knowledge.json` / `role_facts.json` 使用 EDB Circular System 規格（`department_head`，102 facts）。All facts ≤ 80 chars, ≤5 per role key. 39 guideline documents.
4. Release / merge status: **v1.2.2 committed locally，2 commits 待 push**（`git pull --rebase && git push origin main` from Mac terminal）。Repo: `Leonard-Wong-Git/edb-knowledge`. Live URL: https://leonard-wong-git.github.io/edb-knowledge/k1-dashboard.html.
5. Active branch / environment: Single-file HTML (`k1-dashboard.html`, ~2275 lines). INITIAL_DATA 嵌入。TypeScript backend in `backend/`（本地 :8787，未部署）。
6. External platforms / dependencies in scope: EDB website. CDN: React 18.2, Babel 7.23, Tailwind 2.2. Backend deps: openai@4.104.0, tsx, TypeScript. **EDB-AI-Circular-System**（獨立 repo，https://leonard-wong-git.github.io/EDB-AI-Circular-System/edb-dashboard.html）。

## Layer Map
1. Product / System Layer: Dashboard UI, fact data model, review workflow, JSON export, EDB data ingestion, Guidelines Library, Knowledge Platform backend.
2. Development Governance Layer: AGENTS.md session governance, handoff/log protocol.
3. Current task belongs to which layer: Product / System Layer (semantic topic-detection threshold tuned; resuming content review next).
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
1. **[即時]** Push 2 commits to GitHub: `cd ~/Downloads/Claude-edb-knowledge && git pull --rebase && git push origin main`
2. **[次要]** EDB Circular System 接入 knowledge.json — mount EDB-AI-Circular-System repo，寫接入代碼（GitHub Actions 或前端 fetch）
3. **[驗證]** Circular smoke test：用真實 EDB 通告確認 knowledge.json 事實正確注入 AI prompt

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
1. UTC date: 2026-04-04
2. Session ID: Claude_20260404_0700
3. Completed:
   - ✅ 修復 GitHub Pages 白屏（v1.2.2）— INITIAL_DATA 直接嵌入 JS object，移除 AppLoader/fetch
   - ✅ 用戶確認 dashboard 「back to normal」
   - ✅ 分析 EDB 通告智能分析系統（v3.0.4，115 通告，circulars.json 結構）
   - ✅ 確認兩平台 topics 命名對齊，識別 department_head 角色差異
   - ✅ 生成 role_facts.json（EDB 規格，102 facts，驗收 ✅ PASSED）
   - ✅ 生成 knowledge.json 至 repo root（穩定公開接口端點）
   - ✅ §4a 歸檔：SESSION_LOG 869→149 行，Sessions 16–26 → dev/archive/SESSION_LOG_2026_Q2.md
4. Pending: 用戶 push 至 GitHub；EDB Circular System 接入代碼
5. Next priorities (max 3): (1) Push 並確認 knowledge.json 可存取 (2) EDB Circular System 接入 (3) Circular smoke test
6. Risks / blockers: VM push blocked（HTTP 403）；EDB-AI-Circular-System repo 未 mount
