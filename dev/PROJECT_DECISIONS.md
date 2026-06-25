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

### S183 (2026-06-25) — 2 governance rules ship：Supersede ranking penalty 0.05 + Judge bypass extension to vault_extract
- **背景：** S183 ingest VE_CF 2026 主框架 93 chunks + EDBC 3/2026 + EDBCM 221/2025 智啟學教（淨 +108 chunks → 15,644）。Post-deploy Leonard mobile screenshot 反饋 + short-query verification 揭發 2 個 governance-class issue 需要 long-term rule，而非 one-off patch。

- **Rule 1 — Supersede ranking penalty 0.05（Leonard 提出）：**
  - **問題：** Retain-but-rank-down 策略下，舊版（如 values_edu_framework_2021_trial cos=0.794）cosine 自然分高過新版（VE_CF_2026 cos=0.753 差 0.041），令 user 查「價值觀教育」短 query 仍 surface 舊版主導 top-5。
  - **決策：** Backend `searchChannelB.ts` +`SUPERSEDED_IDS` Set + `SUPERSEDE_PENALTY=0.05` const + `applySupersedePenalty()` helper；apply 兩次（main results post-mapping + footnote overlay pre-lead-detection、re-sort 後）；對全 channel（vault_extract + footnote_curated + role_facts）統一 apply。
  - **Penalty 值選擇：** 0.05 empirically — 足夠 swap rank（2021 0.794 → 0.744 < 2026 0.753），但保留 retrieve 命中（學校過渡期仍可能引用舊版）。Below penalty 仍 surface 即係新版 cosine 低過 0.041 + 舊版差太大、retrieve 自然偏好舊版相關度（acceptable）。
  - **SSOT 雙處：** registry `superseded_by` field（authoritative）+ backend `SUPERSEDED_IDS` Set（runtime cache）。Future ingest 新 superseding 版時必同步雙處（同 SOURCE_SETS pattern 一致：每次 manually sync）。
  - **未來擴展點：** 如有更多 superseded sources 累積、可考慮：(a)load registry at startup 自動 build set；(b)`superseded_by_chain` 多層；(c)graduated penalty (例如 2021→0.05、2018→0.08)。當前 KISS 一刀切 0.05 sufficient。
  - **Verified：** 3/3 短 query「價值觀教育」「首要價值觀」「12 首要價值觀」VE_CF 2026 rank 0/1/2、2021 試行版 demoted rank-3+。

- **Rule 2 — Judge bypass extension to vault_extract @ score≥0.70（解 anti-confab over-decline）：**
  - **問題：** S177 anti-confab judge（synthesizeAnswer 之前 binary relevance gate）對 vault_extract chunks 過保守 — 即使 rank-0 score 0.75+（empirically direct topical match）仍 over-decline「未能找到」。Leonard mobile screenshot 報告：「智啟學教是什麼」EDBCM 221 rank-0 0.750 + 「價值觀教育」VE_CF 2021 rank-0 0.794 全 over-declined。
  - **既有 fix（S178）：** footnote_curated lead score ≥ FOOTNOTE_LEAD_SCORE (0.45) bypass judge（hand-curated verbatim-verified direct answer by construction）。但 vault_extract 唔屬於該 class。
  - **決策（S183 擴展）：** +`VAULT_LEAD_SCORE = 0.70` 同 footnote-lead pattern：vault_extract lead score ≥ 0.70 bypass judge。Below 0.70 仍經 judge full protection。
  - **Threshold 0.70 選擇：** S177 凍結教席→IMC-60% confab class 嘅 cosine 喺 **0.55-0.65** range（topically-near-but-wrong）；≥0.70 empirically direct topical match（vault chunks at this cosine reliably answer the query）。0.70 是 confab 同 direct-match 分界 empirical line。
  - **Behavior：** Confab protection retained for marginal cosine 0.50-0.65 case；high-cosine direct match no longer false-decline。3/3 Leonard user query post-fix ANSWER + grounded synthesis。
  - **未來監察：** Monitor false-positive synthesis (vault-lead bypass 但實際 confab 漏網) — 如出現可微調 threshold up 至 0.75。

- **配套 procedural learnings：**
  - **Pre-ingest grep discipline：** S183 漏 catch prior `edbc003_2026` 因為齋 grep brand variant「VE_CF / 價值觀 / value_education」而 prior registry title 短「教育局通告第3/2026號」未含 keyword。Future ingest 之前 grep registry 必同時用 (URL filename pattern + 中文 title keyword + brand variants)。
  - **Short-query verification mandatory：** Per memory `feedback_short_query_first`、real user type 2-4 token query；S183 7+ token long-sentence smoke test 7/8 PASS 但短 query 仍 fail（routing OK 但 judge 過保守）。Post-deploy QC 必驗 2-4 token 短 query。
  - **Pages transient outage remediation：** Pages build/report OK + deploy step fail 4s = GitHub Pages 短暫 outage；standard remediation = empty commit retrigger 即修；workflow status 用 public REST API `https://api.github.com/repos/<owner>/<repo>/actions/runs` 查（公開 repo no auth needed）；gh CLI v2.95.0 已裝、`gh auth login` 後可 read private workflow annotations。
  - **Commits 鏈：** `bc26d41`→`edebbbd`→`40923d5`→`a718a83`→`1359916`→`71f1c80`→`4ddffb6` 全 push origin/main、Render 4 round redeploy + Pages #398 success。

### S176 (2026-06-22) — Agent Handoff Kit v0.3.29 升級：雙治理層共存決策
- **背景**：本專案原用自寫治理（`AGENTS.md` `<INSTRUCTIONS>` §0–§14：PLAN→READ→CHANGE→QC→PERSIST、3-section closeout、`### Next Session Handoff Prompt (Verbatim)` 機制），已運行 175 sessions。S176 升級 Agent Handoff Kit v0.1.7→v0.3.29。
- **決策**：**兩套治理層共存、不取代**。AHK managed-core 追加喺 `<INSTRUCTIONS>` 之後（managed-core BEGIN/END 包圍）；原 §0–§14 全保留。理由：(1) 自寫治理含產品專屬鐵律（凍結合約、display-sync 8 點、Supabase INSPECT 授權、node-fetch pin）AHK 無法涵蓋；(2) AHK 提供 doctor 可驗結構 + rule packs + 機器標記（`ack:`）跨工具續傳。兩者互補。
- **衝突解法（已採用）**：closeout 機制兩者並行——本專案 3-section 輸出（含 `### Next Session Handoff Prompt (Verbatim)` 寫入 SESSION_LOG）+ AHK `START_NEXT_SESSION_PROMPT.txt`（由 handoff `Next Session Opening Message` 區塊重生）。S176 entry 同時保留兩種 startup 區塊。
- **git 追蹤更正（S176 closeout 發現）**：`dev/SESSION_HANDOFF.md`／`SESSION_LOG.md`／`START_NEXT_SESSION_PROMPT.txt` 雖列於 `.gitignore`，但**實際已 git-tracked**（早於 ignore 規則就 commit；`.gitignore` 唔會 untrack 已追蹤檔）。故 S173–S175 每次收工都照常 commit 三者。升級 commit `788538e` 當時誤判為「不入 git」而漏 commit handoff/log 改動 → S176 收工 commit 補回。stale `.gitignore` 規則屬低優先 cleanup（移除該行 or `git rm --cached`，需 Leonard 定）。
- **衝突原則**：AHK core §5「兩 pack 衝突取較安全、較可驗路徑並記錄」。未來如兩層指令矛盾，取較安全可驗者，收工記錄。
- **可驗收據**：`npx @adamchanadam/agent-handoff-kit@latest doctor --root .` → `status: passed`（48 項）。升級備份＋migration report 在 `dev/governance_migrations/20260622T141715Z/`。
- **教訓**：升級遇 2 衝突檔（SESSION_HANDOFF/LOG 因舊自寫格式缺 `ack:` 標記）係**預期**、非錯誤——installer 故意唔覆寫，留 AI 非破壞性補標記（section markers 要放對語義區段，唔可以淨係 cluster 喺檔頭，否則 doctor semantic-placement check 唔過）。
