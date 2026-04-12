# Session Handoff

## Current Baseline
1. Version: **v1.4.0** (K1 EDB Knowledge Platform) — pushed to `main` (commit `318f1f9`)
2. Core commands / features: K1 EDB Knowledge Dashboard (single HTML `k1-dashboard.html`, React 18 + Babel + Tailwind CDN). 107 facts, 7 topics, 全部 approved。Guidelines Library（39 EDB 文件）。**EDB Circular System 接口**：`role_facts.json` (repo root, schema v2.0.0 split-role) 已對齊。
3. Regression baseline: **107 facts**, all approved. `dev/source/source_registry.json` has `148` entries. **[Registry: FULLY HEALTHY]** `check_freshness.py`: Errors: 0 / Checked: 145. **[Online Regression: FULLY PASS]** `npm run regression:semantic`: PASS=12 / FAIL=0.
4. Release / merge status: **v1.4.0 pushed to `main`**. Latest commit: `318f1f9`.
5. Active branch / environment: Single-file HTML + TypeScript backend in `backend/`.
6. External platforms / dependencies in scope: EDB website (URL structure changed 2026-04-12; now monitored via GitHub Actions).

## Version Notes
- Platform version: **v1.4.0** (knowledge.json, guidelines.json, k1-dashboard.html, README)
- `role_facts.json` schema version: **v2.0.0** (split-role; independent of platform version — do NOT overwrite with bump_version.py)

## Layer Map
1. Product / System Layer: Dashboard, fact data model, source registry, freshness monitoring, LLM-wiki pipeline (Phase 3 planned).
2. Development Governance Layer: AGENTS.md protocol.

## Mandatory Start Checklist
1. Read `dev/SESSION_HANDOFF.md`
2. Read `dev/SESSION_LOG.md`
3. Read `dev/CODEBASE_CONTEXT.md`
4. Confirm environment: backend needs `OPENAI_API_KEY` in `backend/.env` at runtime
5. Run baseline checks: `python3 dev/source/check_freshness.py --dry-run`

## Architecture Decision (Session 13 — 2026-03-23)
**Upgrade from keyword RAG → Semantic / Vector RAG (Consultative RAG)**
- `topicDetector.ts` uses OpenAI `text-embedding-3-small` + cosine similarity (`THRESHOLD = 0.45`, `MAX_TOPICS = 2`, `GAP = 0.05`)
- Anti-contamination verified online: PASS=12/12 (2026-04-12)

## Architecture Decision (Session 63 — 2026-04-12)
**LLM-Wiki → Facts pipeline model confirmed:**
- LLM-Wiki = searchable vault of EDB source evidence (statistical facts auto-approved)
- Policy facts = human-gated; LLM proposes from vault evidence, human approves
- Flow: vault extract → LLM proposes candidate fact (with source ref) → human approves → role_facts.json
- This is Phase 3 design (scale-triggered)

## Open Priorities
1. **[Phase 3 設計]** Design the candidate fact proposal pipeline: vault extract → LLM → candidate → Dashboard review UI → role_facts.json
2. **[維護]** GitHub Actions weekly freshness check active — respond to any failure emails promptly
3. **[選擇性]** Expand vault extracts for SAG / Code of Aid / key curriculum guides (enrich LLM-Wiki evidence base)

## Known Risks / Blockers
1. **EDB URL Stability is LOW**: Site restructured 2026-04-12; GitHub Actions weekly check is now the safety net.
2. WebFetch tool cannot access www.edb.gov.hk (EGRESS_BLOCKED) — use browser MCP for research.
3. `bump_version.py` will incorrectly overwrite `role_facts.json` schema version (2.0.0) — always restore after bumping.
4. Backend: `OPENAI_API_KEY` required in `backend/.env` for online ops (file is gitignored).

## Regression / Verification Notes
1. All core 2024/2025 curriculum guides verified and reachable ✅.
2. All 9 round-2 legacy PSHE/Arts PDF URLs confirmed ✅.
3. `check_freshness.py` result: **Errors: 0 / Checked: 145** ✅.
4. **Online semantic regression: PASS=12 / FAIL=0** (mode: online-capable, 2026-04-12) ✅.
5. GitHub Actions CI: weekly freshness check active (every Monday 09:00 UTC) ✅.

## Source Audit Summary (v1.4.0 baseline)
All 148 registry entries reachable as of 2026-04-12. All KLAs fully verified.

## Consolidation Watchlist
- `bump_version.py` — needs a fix to exclude `role_facts.json` from platform version bumps (known gotcha, document for next session).

## Update Rule
This file and `dev/SESSION_LOG.md` must be updated at the end of every session.

## Last Session Record
1. UTC date: 2026-04-12
2. Session ID: Antigravity_20260412_1900
3. Completed:
   - ✅ **[Online Regression]** PASS=12/FAIL=0 verified with real OPENAI_API_KEY.
   - ✅ **[GitHub Actions CI]** Weekly freshness check automated (every Monday 09:00 UTC).
   - ✅ **[v1.4.0]** Platform version bumped and pushed to `main` (commit `318f1f9`).
   - ✅ **[Architecture]** Phase 3 LLM-Wiki → facts pipeline model confirmed (evidence-first, human-gated).
4. Pending: Phase 3 design; vault extract expansion.
5. Next priorities (max 2): (1) Phase 3 candidate fact pipeline design (2) vault extract expansion.
6. Risks / blockers: bump_version.py gotcha with role_facts.json schema version.

