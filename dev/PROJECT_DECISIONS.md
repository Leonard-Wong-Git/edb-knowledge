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

# Project Decisions Log

這個檔保存項目的長期演進、決策、架構取捨與學習觀察 narrative。屬 warm 資料層 —— AI 開工**不需要讀**本檔。

🔹 短期 single-task project：本檔保持近空，你不需要 maintain
🔹 長期持續演進項目：AI 會在收工時先做維護觸發檢查；命中觸發或到定期兜底時才完整整理。當你問「我們之前為何這樣做」時，AI 會在這裡找答案

不需要你手動寫 —— AI 在收工時自動 update；重大決策可在發生時即時記錄，不必等到最後才回想。

Research-derived decisions use this compact evidence-chain format inside the relevant section, without creating a new section:

```text
- YYYY-MM-DD [research-derived] Decision summary. Evidence chain: Source=source:<id>; Summary=<source finding>; Inference=<reasoning>; Decision impact=<what changed>; Uncertainty=<limits or none>.
```

The `source:<id>` token must also appear in `dev/PROJECT_INDEX.md` under `Fact Base` or `External Sources`, so later sessions can trace the decision back to its source map.

This file does not store raw build / upload / QC evidence, current next actions, one-time task results, or reusable operating procedures. Keep those in `dev/SESSION_LOG.md`, `dev/SESSION_HANDOFF.md`, or the relevant rule pack / registered reference.

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

---

## Decisions Archive

(empty)

## Insights & Learnings

### S176 (2026-06-22) — Agent Handoff Kit v0.3.29 升級：雙治理層共存決策
- **背景**：本專案原用自寫治理（`AGENTS.md` `<INSTRUCTIONS>` §0–§14：PLAN→READ→CHANGE→QC→PERSIST、3-section closeout、`### Next Session Handoff Prompt (Verbatim)` 機制），已運行 175 sessions。S176 升級 Agent Handoff Kit v0.1.7→v0.3.29。
- **決策**：**兩套治理層共存、不取代**。AHK managed-core 追加喺 `<INSTRUCTIONS>` 之後（managed-core BEGIN/END 包圍）；原 §0–§14 全保留。理由：(1) 自寫治理含產品專屬鐵律（凍結合約、display-sync 8 點、Supabase INSPECT 授權、node-fetch pin）AHK 無法涵蓋；(2) AHK 提供 doctor 可驗結構 + rule packs + 機器標記（`ack:`）跨工具續傳。兩者互補。
- **衝突解法（已採用）**：closeout 機制兩者並行——本專案 3-section 輸出（含 `### Next Session Handoff Prompt (Verbatim)` 寫入 SESSION_LOG）+ AHK `START_NEXT_SESSION_PROMPT.txt`（由 handoff `Next Session Opening Message` 區塊重生）。S176 entry 同時保留兩種 startup 區塊。
- **git 追蹤更正（S176 closeout 發現）**：`dev/SESSION_HANDOFF.md`／`SESSION_LOG.md`／`START_NEXT_SESSION_PROMPT.txt` 雖列於 `.gitignore`，但**實際已 git-tracked**（早於 ignore 規則就 commit；`.gitignore` 唔會 untrack 已追蹤檔）。故 S173–S175 每次收工都照常 commit 三者。升級 commit `788538e` 當時誤判為「不入 git」而漏 commit handoff/log 改動 → S176 收工 commit 補回。stale `.gitignore` 規則屬低優先 cleanup（移除該行 or `git rm --cached`，需 Leonard 定）。
- **衝突原則**：AHK core §5「兩 pack 衝突取較安全、較可驗路徑並記錄」。未來如兩層指令矛盾，取較安全可驗者，收工記錄。
- **可驗收據**：`npx @adamchanadam/agent-handoff-kit@latest doctor --root .` → `status: passed`（48 項）。升級備份＋migration report 在 `dev/governance_migrations/20260622T141715Z/`。
- **教訓**：升級遇 2 衝突檔（SESSION_HANDOFF/LOG 因舊自寫格式缺 `ack:` 標記）係**預期**、非錯誤——installer 故意唔覆寫，留 AI 非破壞性補標記（section markers 要放對語義區段，唔可以淨係 cluster 喺檔頭，否則 doctor semantic-placement check 唔過）。
