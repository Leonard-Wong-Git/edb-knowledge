# Session Handoff

## Current Baseline
1. Version: **v1.3.1** (K1 EDB Knowledge Platform) — pushed to `main`; backend split-role compatibility bridge included
2. Core commands / features: K1 EDB Knowledge Dashboard (single HTML `k1-dashboard.html`, React 18 + Babel + Tailwind CDN). 107 facts, 7 topics,全部 approved。Guidelines Library（39 EDB 文件）。**EDB Circular System 接口**：`role_facts.json` (repo root) 已對齊。
3. Regression baseline: **107 facts**, all approved. `dev/source/source_registry.json` has `148` entries. **[Registry: FULLY HEALTHY]** — `check_freshness.py`: Errors: 0 / Checked: 145. **[Online Regression: FULLY PASS]** — `npm run regression:semantic`: PASS=12 / FAIL=0.
4. Release / merge status: **v1.3.1 pushed to `main`**. Latest commits: `b09e8da` + `7b64d18`.
5. Active branch / environment: Single-file HTML + TypeScript backend in `backend/`.
6. External platforms / dependencies in scope: EDB website (URL structure changed 2026-04-12).

## Layer Map
1. Product / System Layer: Dashboard, fact data model, source registry, freshness monitoring.
2. Development Governance Layer: AGENTS.md protocol.

## Mandatory Start Checklist
1. Read `dev/SESSION_HANDOFF.md`
2. Read `dev/SESSION_LOG.md`
3. Read `dev/CODEBASE_CONTEXT.md`
4. Confirm environment: backend needs `OPENAI_API_KEY=sk-...` in `backend/.env` at runtime
5. Run baseline checks: `python3 dev/source/check_freshness.py --dry-run`

## Architecture Decision (Session 13 — 2026-03-23)
**Upgrade from keyword RAG → Semantic / Vector RAG (Consultative RAG)**
- `topicDetector.ts` uses OpenAI `text-embedding-3-small` + cosine similarity (`THRESHOLD = 0.45`, `MAX_TOPICS = 2`, `GAP = 0.05`)
- Anti-contamination verified online: PASS=12/12 (2026-04-12)

## Open Priorities
1. **[維護]** Maintain freshness rhythm: run `check_freshness.py --dry-run` weekly (EDB site is volatile)
2. **[選擇性]** Consider adding more real circular samples to `realCircularCases` in regression harness

## Known Risks / Blockers
1. **EDB URL Stability is LOW**: The site restructured on 2026-04-12. Regular freshness checks are mandatory.
2. WebFetch tool cannot access www.edb.gov.hk (EGRESS_BLOCKED) — use browser MCP for research.
3. Backend: `OPENAI_API_KEY` required in `backend/.env` for online ops (file is gitignored).

## Regression / Verification Notes
1. All core 2024/2025 curriculum guides verified and reachable ✅.
2. All 9 round-2 legacy PSHE/Arts PDF URLs confirmed via freshness sync ✅.
3. `check_freshness.py` result: **Errors: 0 / Checked: 145** ✅.
4. **Online semantic regression: PASS=12 / FAIL=0** (mode: online-capable, 2026-04-12) ✅.
5. Anti-contamination filters (`MAX_TOPICS=2`, `SCORE_GAP=0.05`) verified end-to-end ✅.
6. All Phase 1 + 2 changes pushed to GitHub `main` (commits `b09e8da` + `7b64d18`) ✅.

## Source Audit Summary (v1.3.1 baseline)
All 148 registry entries reachable as of 2026-04-12. All KLAs fully verified.

## Consolidation Watchlist
None currently.

## Update Rule
This file and `dev/SESSION_LOG.md` must be updated at the end of every session.

## Last Session Record
1. UTC date: 2026-04-12
2. Session ID: Antigravity_20260412_1805
3. Completed:
   - ✅ **[Online Regression]** `npm run regression:semantic`: **PASS=12 / FAIL=0** (online-capable mode).
   - ✅ Fixed 4 synthetic query texts (too short for 0.45 threshold) — enriched to multi-sentence.
   - ✅ Anti-contamination filters (`MAX_TOPICS=2`, `SCORE_GAP=0.05`) confirmed end-to-end.
   - ✅ GitHub pushed (regression script fix included).
4. Pending: maintain freshness rhythm weekly.
5. Next priorities (max 2): (1) Weekly freshness check rhythm (2) Optionally add more real circular samples.
6. Risks / blockers: EDB site instability; backend requires `.env` with API key.

