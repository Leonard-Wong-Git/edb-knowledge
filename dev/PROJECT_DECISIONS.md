# Project Decisions — EDB K1 知識平台

> Long-term architecture choices, multi-option trade-offs, and cross-session evolution.
> Created S145 (§4 trigger c: Q4 Phase 2 completion).

---

## Architecture Choices

### ADR-001 — Channel B Downstream Integration Model (Q4 Phase 2)
- **Date**: 2026-06-05 (S144 model decision; S145 build + verified live)
- **Status**: IMPLEMENTED + LIVE
- **Context**: Channel A (`knowledge.json` @455 facts, frozen Q4 Phase 1) previously fed Circular System. Q4 Phase 2 = transition downstream to Channel B (Supabase `wiki_chunks` 10,594 chunks, pgvector).
- **Options considered**:
  - A: Export full snapshot (batch file) → ❌ conflicts with near-real-time freshness goal
  - B: Pure query-time API (downstream calls K1 `/api/search/channel-b` per query) → ⚠️ binds downstream to onrender free-tier (cold-start ~30s, 10 req/min/IP, no SLA)
  - **C (chosen): Incremental sync / manifest-diff delta feed** → downstream maintains its own vector index, polls K1 manifest for id-set delta, queries locally. Avoids both snapshot staleness and free-tier dependency.
- **Decision driver**: Downstream Circular System profile confirmed S145 = GitHub Actions ephemeral cron 3×/day + file-based numpy (NOT persistent service / NOT pgvector). Incremental sync avoids re-embedding 10K chunks per cron run; ETag/304 + delta minimises bandwidth.
- **Implementation**: `backend/src/api/channelBSync.ts` — `GET /api/channel-b/manifest` + `POST /api/channel-b/chunks`; X-Sync-Key gated; anon-REST; NO CORS; own 60/min + daily chunk budget. Contract = `dev/CHANNEL_B_SYNC_SPEC.md` v0.5.
- **Evidence chain**: S144 model selection (3 options, downstream profile gathering) → S145 downstream reply (embedding path-1 confirmed, 3 reverse-questions answered) → 5-lens adversarial review (40 agents, 4 real fixes) → live smoke PASS (anon reads `embedding` 1536-vec, all 13 fields present). Spec v0.3→v0.5.
- **Uncertainty / watch**: manifest O(N) full-table scan shares free-tier DB budget with live search (§8 spec); cache singleflight + TTL mitigates; monitor for 57014 degradation. Daily budget is soft (in-memory, resets on restart). anon key reading `embedding` column confirmed live (was load-bearing assumption until S145 smoke).
- **Rollback**: `git revert` channelBSync.ts + 2 route lines in server.ts; remove `CHANNEL_B_SYNC_KEY` Render env → endpoint returns 503. Supabase/Channel A/pipeline untouched.

---

## Evolution Timeline

### S143 (2026-06-05) — Q4 Phase 1: Channel A Frozen
- `knowledge.json` stopped at @455 facts; schema unchanged; downstream zero-impact.
- Guidelines.json NOT frozen; continues live @152 v2.5.0.
- All Channel A endpoints remain (dormant); reversible via git revert docs.

### S145 (2026-06-05) — Q4 Phase 2 K1-side Complete
- Channel B sync endpoints built, adversarially reviewed, deployed, live smoke passed.
- Downstream (Circular System) to build its own consumer from spec v0.5 + sync key.
- Channel A remains frozen; Channel B search remains live; no data mutations.
